import json
from ArtemusPark.database.db_connection import get_connection
from ArtemusPark.service.Crypto_Service import CryptoService


class ChatRepository:
    def get_chats_for_user(self, dni):
        """Returns all chats the user is part of with unread message count.
        If it's a 2-person chat, the name is the other participant's name."""
        conn = get_connection()
        try:
            cursor = conn.cursor(dictionary=True, buffered=True)
            query = """
                    SELECT c.id_chat,
                           CASE 
                               WHEN (SELECT COUNT(*) FROM User_Chat uc2 WHERE uc2.id_chat = c.id_chat) = 2 THEN
                                   (SELECT COALESCE(NULLIF(u.full_name, ''), u.username)
                                    FROM User_Chat uc3
                                    JOIN User u ON uc3.dni = u.dni
                                    WHERE uc3.id_chat = c.id_chat AND uc3.dni != %s)
                               ELSE c.name
                           END as name,
                           ((SELECT COUNT(*) FROM User_Chat uc4 WHERE uc4.id_chat = c.id_chat) > 2) as is_group,
                           c.created_at,
                           (SELECT COUNT(*)
                            FROM Message m
                            WHERE m.id_chat = c.id_chat
                              AND m.sender_dni != %s
                              AND m.is_read = FALSE) as unread_count
                    FROM Chat c
                             JOIN User_Chat uc ON c.id_chat = uc.id_chat
                    WHERE uc.dni = %s
                    """
            cursor.execute(query, (dni, dni, dni))
            return cursor.fetchall()
        finally:
            conn.close()

    def get_messages_in_chat(self, id_chat, current_user_dni):
        """Returns all messages in a specific chat with sender info and marks them as read."""
        conn = get_connection()
        try:
            cursor = conn.cursor(dictionary=True, buffered=True)
            # Mark messages not sent by me as read
            cursor.execute(
                "UPDATE Message SET is_read = TRUE WHERE id_chat = %s AND sender_dni != %s",
                (id_chat, current_user_dni),
            )
            conn.commit()

            # First attempt: Try to get raw content (some might be RSA JSON)
            query = """
                    SELECT m.id_message,
                           m.content as raw_content,
                           CAST(AES_DECRYPT(UNHEX(m.content), 'artemus_master_key') AS CHAR) as aes_content,
                           m.sent_at,
                           u.dni as sender_dni,
                           u.username,
                           u.full_name,
                           r.role as sender_role,
                           m.is_read
                    FROM Message m
                             JOIN User u ON m.sender_dni = u.dni
                             JOIN Role r ON u.id_role = r.id_role
                    WHERE m.id_chat = %s
                    ORDER BY m.sent_at ASC \
                    """
            cursor.execute(query, (id_chat,))
            messages = cursor.fetchall()

            for msg in messages:
                if msg["aes_content"]:
                    msg["content"] = msg["aes_content"]
                else:
                    msg["content"] = msg["raw_content"]

            return messages
        finally:
            conn.close()

    def update_chat_name(self, id_chat, new_name):
        """Updates the name of a chat."""
        conn = get_connection()
        try:
            cursor = conn.cursor(buffered=True)
            cursor.execute(
                "UPDATE Chat SET name = %s WHERE id_chat = %s", (new_name, id_chat)
            )
            conn.commit()
        finally:
            conn.close()

    def delete_chat(self, id_chat):
        """Deletes a chat and all its messages (cascade)."""
        conn = get_connection()
        try:
            cursor = conn.cursor(buffered=True)
            cursor.execute("DELETE FROM Chat WHERE id_chat = %s", (id_chat,))
            conn.commit()
        finally:
            conn.close()

    def get_total_unread_count(self, user_dni):
        """Returns the number of unread messages for the user across all chats."""
        conn = get_connection()
        try:
            cursor = conn.cursor(buffered=True)
            query = """
                    SELECT COUNT(*)
                    FROM Message m
                             JOIN User_Chat uc ON m.id_chat = uc.id_chat
                    WHERE uc.dni = %s
                      AND m.sender_dni != %s
                      AND m.is_read = FALSE \
                    """
            cursor.execute(query, (user_dni, user_dni))
            res = cursor.fetchone()
            return res[0] if res else 0
        finally:
            conn.close()

    def send_message(self, id_chat, sender_dni, content):
        """Inserts a message. Uses RSA for private chats (if keys exist), AES for others."""
        conn = get_connection()
        try:
            cursor = conn.cursor(dictionary=True, buffered=True)

            # Get participants and their public keys
            cursor.execute(
                "SELECT u.dni, u.public_key FROM User u JOIN User_Chat uc ON u.dni = uc.dni WHERE uc.id_chat = %s",
                (id_chat,),
            )
            participants = cursor.fetchall()

            # Check if everyone in the chat has a public key
            all_have_keys = all(p["public_key"] for p in participants)

            if id_chat != 1 and len(participants) <= 5 and all_have_keys:
                # RSA Strategy: Encrypt for each participant
                payload = {}
                for p in participants:
                    try:
                        encrypted = CryptoService.encrypt_with_public_key(
                            content, p["public_key"]
                        )
                        payload[p["dni"]] = encrypted
                    except:
                        continue

                envelope = {"type": "rsa", "payload": payload}
                final_content = json.dumps(envelope)
                query = "INSERT INTO Message (id_chat, sender_dni, content) VALUES (%s, %s, %s)"
                cursor.execute(query, (id_chat, sender_dni, final_content))
            else:
                # AES Strategy (Legacy / Fallback): Use the master key
                # This ensures we don't lose communication if someone hasn't migrated yet
                query = """
                    INSERT INTO Message (id_chat, sender_dni, content)
                    VALUES (%s, %s, HEX(AES_ENCRYPT(%s, 'artemus_master_key'))) 
                """
                cursor.execute(query, (id_chat, sender_dni, content))

            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()

    def create_chat(self, name, participants_dni):
        """Creates a new chat and adds participants."""
        conn = get_connection()
        try:
            cursor = conn.cursor(buffered=True)
            cursor.execute("INSERT INTO Chat (name) VALUES (%s)", (name,))
            chat_id = cursor.lastrowid

            for dni in participants_dni:
                cursor.execute(
                    "INSERT INTO User_Chat (dni, id_chat) VALUES (%s, %s)",
                    (dni, chat_id),
                )

            conn.commit()
            return chat_id
        finally:
            conn.close()

    def get_all_users_for_chat_start(self, current_user_dni):
        """Returns all active users except the current one."""
        conn = get_connection()
        try:
            cursor = conn.cursor(dictionary=True, buffered=True)
            query = "SELECT dni, username, full_name FROM User WHERE active = TRUE AND dni != %s"
            cursor.execute(query, (current_user_dni,))
            return cursor.fetchall()
        finally:
            conn.close()

    def get_participants_in_chat(self, id_chat):
        """Returns all users in a specific chat."""
        conn = get_connection()
        try:
            cursor = conn.cursor(dictionary=True, buffered=True)
            query = """
                SELECT u.dni, u.username, u.full_name 
                FROM User u
                JOIN User_Chat uc ON u.dni = uc.dni
                WHERE uc.id_chat = %s
            """
            cursor.execute(query, (id_chat,))
            return cursor.fetchall()
        finally:
            conn.close()

    def add_user_to_chat(self, id_chat, dni):
        """Adds a user to an existing chat."""
        conn = get_connection()
        try:
            cursor = conn.cursor(buffered=True)
            cursor.execute(
                "INSERT IGNORE INTO User_Chat (dni, id_chat) VALUES (%s, %s)",
                (dni, id_chat),
            )
            conn.commit()
        finally:
            conn.close()

    def remove_user_from_chat(self, id_chat, dni):
        """Removes a user from a chat."""
        conn = get_connection()
        try:
            cursor = conn.cursor(buffered=True)
            cursor.execute(
                "DELETE FROM User_Chat WHERE dni = %s AND id_chat = %s", (dni, id_chat)
            )
            conn.commit()
        finally:
            conn.close()
