-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Servidor: 127.0.0.1
-- Tiempo de generación: 20-05-2026 a las 18:05:00
-- Versión del servidor: 12.2.2-MariaDB
-- Versión de PHP: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de datos: `artemus`
--

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `air_quality`
--

CREATE TABLE `air_quality` (
  `id_measurement` int(11) NOT NULL,
  `co2_level` float NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `chat`
--

CREATE TABLE `chat` (
  `id_chat` int(11) NOT NULL,
  `name` varchar(100) DEFAULT NULL,
  `created_at` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

--
-- Volcado de datos para la tabla `chat`
--

INSERT INTO `chat` (`id_chat`, `name`, `created_at`) VALUES
(1, 'Global', '2026-05-19 14:05:41'),
(2, 'Chat', '2026-05-20 14:45:21'),
(3, 'Chat', '2026-05-20 14:45:26'),
(4, 'Chat', '2026-05-20 14:46:06');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `door_control`
--

CREATE TABLE `door_control` (
  `id_measurement` int(11) NOT NULL,
  `is_open` tinyint(1) NOT NULL DEFAULT 0,
  `access_direction` varchar(10) DEFAULT NULL,
  `user_dni` varchar(20) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `humidity`
--

CREATE TABLE `humidity` (
  `id_measurement` int(11) NOT NULL,
  `humidity` float NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `lighting`
--

CREATE TABLE `lighting` (
  `id_measurement` int(11) NOT NULL,
  `is_on` tinyint(1) NOT NULL DEFAULT 0,
  `power_watts` float DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `measurement`
--

CREATE TABLE `measurement` (
  `id_measurement` int(11) NOT NULL,
  `id_sensor` int(11) NOT NULL,
  `timestamp` datetime DEFAULT current_timestamp(),
  `description` varchar(255) DEFAULT NULL,
  `elec_consumption` float DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `message`
--

CREATE TABLE `message` (
  `id_message` int(11) NOT NULL,
  `id_chat` int(11) NOT NULL,
  `sender_dni` varchar(20) NOT NULL,
  `content` text NOT NULL,
  `sent_at` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `permission`
--

CREATE TABLE `permission` (
  `id_permission` int(11) NOT NULL,
  `description` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

--
-- Volcado de datos para la tabla `permission`
--

INSERT INTO `permission` (`id_permission`, `description`) VALUES
(7, 'ACCESS_ADMIN_PANEL'),
(9, 'ACTIVATE_EMERGENCY'),
(4, 'MANAGE_REQUESTS'),
(6, 'MANAGE_SENSORS'),
(8, 'MANAGE_USERS'),
(1, 'VIEW_DASHBOARD'),
(2, 'VIEW_HISTORY'),
(5, 'VIEW_MAINTENANCE'),
(3, 'VIEW_REQUESTS');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `role`
--

CREATE TABLE `role` (
  `id_role` int(11) NOT NULL,
  `role` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

--
-- Volcado de datos para la tabla `role`
--

INSERT INTO `role` (`id_role`, `role`) VALUES
(1, 'admin'),
(2, 'maintenance'),
(3, 'user');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `role_permission`
--

CREATE TABLE `role_permission` (
  `id_role` int(11) NOT NULL,
  `id_permission` int(11) NOT NULL,
  `assigned_at` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

--
-- Volcado de datos para la tabla `role_permission`
--

INSERT INTO `role_permission` (`id_role`, `id_permission`, `assigned_at`) VALUES
(1, 1, '2026-05-19 14:05:40'),
(1, 2, '2026-05-19 14:05:40'),
(1, 3, '2026-05-19 14:05:40'),
(1, 4, '2026-05-19 14:05:40'),
(1, 5, '2026-05-19 14:05:40'),
(1, 6, '2026-05-19 14:05:40'),
(1, 7, '2026-05-19 14:05:40'),
(1, 8, '2026-05-19 14:05:40'),
(1, 9, '2026-05-19 14:05:40'),
(2, 1, '2026-05-19 14:05:40'),
(2, 2, '2026-05-19 14:05:40'),
(2, 3, '2026-05-19 14:05:40'),
(2, 4, '2026-05-19 14:05:40'),
(2, 5, '2026-05-19 14:05:40'),
(2, 6, '2026-05-19 14:05:40'),
(3, 1, '2026-05-19 14:05:40');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `sensor`
--

CREATE TABLE `sensor` (
  `id_sensor` int(11) NOT NULL,
  `id_zone` int(11) NOT NULL,
  `id_type` int(11) NOT NULL,
  `id_role` int(11) NOT NULL,
  `name` varchar(100) NOT NULL,
  `active` tinyint(1) DEFAULT 1,
  `created_at` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `sensor_ordinario`
--

CREATE TABLE `sensor_ordinario` (
  `id_measurement` int(11) NOT NULL,
  `valor_numerico` int(11) NOT NULL,
  `valor_texto` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `temperature`
--

CREATE TABLE `temperature` (
  `id_measurement` int(11) NOT NULL,
  `temperature` float NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `ticket`
--

CREATE TABLE `ticket` (
  `id_ticket` int(11) NOT NULL,
  `user_dni` varchar(20) NOT NULL,
  `type` varchar(50) DEFAULT 'MAINTENANCE',
  `description` varchar(255) NOT NULL,
  `status` varchar(20) DEFAULT 'PENDING',
  `created_at` datetime NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `type`
--

CREATE TABLE `type` (
  `id_type` int(11) NOT NULL,
  `description` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

--
-- Volcado de datos para la tabla `type`
--

INSERT INTO `type` (`id_type`, `description`) VALUES
(4, 'Air_Quality'),
(6, 'Door'),
(2, 'Humidity'),
(5, 'Lighting'),
(7, 'Sensor_Ordinario'),
(1, 'Temperature'),
(3, 'Wind');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `user`
--

CREATE TABLE `user` (
  `dni` varchar(20) NOT NULL,
  `id_role` int(11) NOT NULL,
  `username` varchar(50) NOT NULL,
  `full_name` varchar(100) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `phone` varchar(20) DEFAULT NULL,
  `address_street` varchar(100) DEFAULT NULL,
  `address_city` varchar(50) DEFAULT NULL,
  `address_zip` varchar(10) DEFAULT NULL,
  `profile_picture` longblob DEFAULT NULL,
  `public_key` text DEFAULT NULL,
  `private_key` text DEFAULT NULL,
  `active` tinyint(1) DEFAULT 1,
  `created_at` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

--
-- Volcado de datos para la tabla `user`
--

INSERT INTO `user` (`dni`, `id_role`, `username`, `full_name`, `password_hash`, `phone`, `address_street`, `address_city`, `address_zip`, `profile_picture`, `public_key`, `private_key`, `active`, `created_at`) VALUES
('12345678p', 3, 'rd', 'rodrigo', 'a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3', '600500802', '', '', '', NULL, '-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAkjlGNHpxL1il0DB97iKv\n4iwTZNyrcrpjzGaf1AM/lVlR+bqg6TM4xIYgdRcW9RFVc3+VhGCCd3qBNKaxFUxD\nIsRbZYzdpRPaICji3r+gSpr7CrKAMLWot05vAblTINpuoj2gzDqqegc002J5o3dz\n4GXK4KV83E2dGrz0rVQHEm/ajRdzB8lMxvhDQmMcsWU1jPZMdjNxfSEyxHelO4Cs\n8FzsuI/6HGlG3F0TV825UITtUAEa1DtnJLkA6Mz8+gGw9MOPm3ho9kQztZ2Eyo9v\n2wB5iHQLlucztigGwqbxg7ugOSOMyLZCCdmrB7mBFotZBo69UtZ5kAjj/pyGn/BK\nYwIDAQAB\n-----END PUBLIC KEY-----\n', 'gAAAAABqDa0J5B4aLD71NuFxcW7Ke8sSwG6vC-RdAFc-c0iOxbDnHFfS-yBW92Nde3Eikk2-ozqBE5ZodvZlubk0bCgxrFhaQpHNtsAm8hOs2LenUEVfefeSY3K6SGt0RY4Rn_JH4lbj80D88-5BKl07biQhC3b9EVt7p1H-JKlP7iWspZBJyS5yFZLMyjvvNXP2fXU4HGhD-li4vUhONvYYi2hYGDxFzbaTxFvOGMF6WmxPREIitQs79B6Apq089Y4kPWsHvXjvbRP6brLjTdSPm0S8HHvacKphc7haZu70f3rDSnt_5GIz9g129isUOgM78TduAyOTffZPuPDNhxgURmk6FSI_NnyAySDbkn2lS-ufPxLITRdaOAo-cWWJcb3TNPIIZSNpkVOmvUIVkyM0zIVBA0bZq0MQauWrQ629UkZ0iLYeXN4GvcV96YLmGZ5UWuVz3mWkubB4IgRJskyr9YpkjmrpjX0VeD2jY7wiv8I8X3M0Di-d0BA02JtvzvlErFDtpAGJDkC_S7d-nVD2DztDElcrx8vZ4az6aXJcF1JhnoFHSMME5dbSmb1Aw9-4EJCjYuV4zyL6LeAUAIi-1QI1Y8MurnrTp3nrZ8GvStVgZi41yNXcgMkxUbKhfNZFueU8CVTSxQuCHqd-JMPu5X3mgy-qbNrTeZLtSSDsCirHVY18z1OzEzhqfrGxKDTXOn9AEfAtip66mYWd6pRRi5AGi9cqIj-fa9IaXJsApiiKqg4g_jv2Lf2RgvLSDGYfkvX1l20hfdrowdp-Iqt1wU_Gi3VOTlndC1-ijqYdBh6PvKFxG3QPQxXzjvZ_8Dvw6nltzKEQtCrcKKafEq3l4YsDkvy5-XMdBw1nlFpN2F66bOWJ6qQ_zVBtAYUI8kDXrL9BPDTBqJEF-h_S54_vUZhTWEkINDIyMIgJ0nWPZHJrqGvCBw0xm57o0oGCRx6B_pm-QTtSUJ9b-5StLnVw6JAalwVcb-3HD6ZSNSqmqRJ5p2aDPQZcc9sME8DkzX9oF6MqHn8tUc3kM4VDtZSCKVSsvio5DigZN0ckHx3ynsyMXp_80Mex04mZ10eCsEopDGZjp0uhnpQCcDV-tW6TzOhszgGsP2RIeSlQyX6vPROW4c95MbXf46KMwFAER3ZZDu7kxKkkmiU8rXzQNybpJsk_iZwvEq1S-6WspjyTo4rO779caiaZGNFH01QlL_hMXtcBhlr8BTkT6bEWsD7PvugZX1yAHrBwAzRmhxQJscw65bx_mPadJ02e8cSypWTjg52qdTr0pbhVjk2xaoupaoTJf9oeivltPyTghqsjbexiGjIy7bI86n6chN2kMPgAqLGMITnBW7A3bijB0HF5VWxCb3a5fjLcrET_O099pfqLXrj-GZT120HTCDoLM5cYe3qC4LBDeO_gL3NNwIOZy3Hf-TVGkj40q2VsWjv82d28VtMW5dpR9K6_N3LC6yqsojgTpimZwG_v-ObMy5J3UMM7rdVBSamYL7o7g-6zTIgk9RiyWPqYawChbQglJ0ZAPhsCtzyf5eGFh6PX-thNigcLSP_w48vclCRoezFpmUrkRwies1X9zrb4lsr0rdg_qFa1j3-npSyza508fCsjJwKYW0tqKQzobHUuQrDhPN02Q05Q0QSI9fqUq_6Wq2VyYOMmHvUMISeKEnF0GcUEs6nn8qiDkS_XGEHN0VEOU7X8NcAwMK3vDUO4mTP2CSnCgcgeWPAXQy77UjMTinJET4RoqPIwjZEe2_j7ykItQ0-xNAxHo8gcunHYe2qbYPSKjdDPVH_fI3k21p7V43Y2rYevebje3YGljnLRVrUGnYOcQVAu7bLn1NVva1dH1UFPfe9QXsBa1JS0--4dTyeIa5kBN6rKA48Yzkd13-y4NLzAi_tIwJPQ-1vHNlNgZq9hJtXY7haYmKfnXXeJCN-eQgz0eDgYGVALaB_RUsPtvovjat87h-V1VUc__3PQeFoAok-Esfd_hyjMWbZ7voeHJIn7FLDcMqDD9BgO1tPo5FdNGqTM4OgefIdAIH9Pq9AZzyf_Gj9tBBnB-TyIUUOPl_8Hfqu4WqV95NX5JvNmxsPk0LegJZn8bIkYyr_rH5UmXos13BGad-JUbUd4xndTlqkbqQU7ImLVTEjvb6ibF5iEJTx1CsHR6dpmImO1d9OAVcdJcZ1dOjH2vqGlMNfTGcjvnj1ETIr8F8cqCJWNUFiK2OsSH87kaVJ6D_oFLj5VqWyzWlTR1GcEBn1dBvzeHwYwZoHSZ5jq1dSzxgZqGQNnIdKHY-nvhM16Rjv3x-_ooKVAbIk2cE-TjArslCaBzVdN7JYyXZWKevRVOPFg43TCMy4PWs0=', 1, '2026-05-20 14:37:58'),
('12345678X', 1, 'admin_aldo', 'Aldo Daniel', 'a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3', NULL, 'Central Ave 45', 'Madrid', '28001', NULL, '-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAufYhr4BOBukQ4pXr/nTW\nAgtBtMHggzqZ+U7HHCOr73TNejyxUyIkc0Tn2tmjnfmIQSbo53zgsXA7BObzGPrr\nHcm8dmywHGZJl17dM9VBGRekQm8IHPq+u8AXZJEuRsxU4V5u7xw5/kyOPSFa2jhy\nTHSomaWup3VW5GHlgPS0JIP4xrOwuW5ZODYYjlMm4NlwNt1unO+/+OWL/IMTI2WR\ny8uqXdDUIh09B3CuFYutJSq9VeDz/K9XT2b200ISQ+ZNo/hm0wg9Af8/N//7nsW5\nZvsJ30om9O/z6XRdOZGwyOFYE2WCNRqGMP+T2WocEcL+Wzxaer3swTUKPcnGJUPN\nwwIDAQAB\n-----END PUBLIC KEY-----\n', 'gAAAAABqDayNRBkm7Snl27R9p0UNLvUT8nR9XhZXDGqPCy2T9pX0Tgf1EG5Z5xfhj2Nx-CaCJAxVsA_KNyHnh7Vl8pjFqMISR5vn6uZG1sUJLuIxImT9qJFHjFHSvxuShwCTv7FkPqI0SfYxBXL_wvU7ctAPUr5dt_k21yw77_pFxonRIR8JS-Q66o5JuDmCJgQF52qA-u-7FZzSrGD_f4oWoc4P_GlgLeiMPb5PiSUfHBiqAdrVg82MAfR2kTbg9Sik5v-JQh_yBPCy6xGZL92Rqeg_zztjDESXD2B8-t3Xq0u1I4ZQMYJK7qFYMkIz4mqvYLpTpQXJnPR20BTj_ZeXCVQt-WpdsrECF-DAukR98svi1xu9hCfn-i5ZaeJHKwat5h7KTWQo-oyl0HrlO-IwVX0eg-2brUM7R6xQr6uGAAWz2JYiA8UI6FR66UH9hE5BQATwlPc6WkyZ9biIjCBbTn01vJcBJibL2EhERECS2XWFNDIUtCfUMVO28dVMZPKhphA--_rDOkBEP5W9GMarjVRhckasR6yGg7-XTNbJAt2o8rhZl4N1GoePb7cEah96Of15fvdLPPzVQ32w0QQPY2VBVulH6Jfe5PkJwz63xyQphqi9q9sWzcvT0aH8u0DzloAA9yKtQilj5YRr-lyhu-tvyDc0DXeuskMcX1HX13U2e-O1WBS03-Zsusul9VGWf5cbtEqqgy2Af9feQtYkQUylxF8gFQ2mBrXRDw-la_JkgDn6rmvpj8aLdrWexjcyjmz1-mMriZ-TrDFwfy5KDNELElkCUV4JSQhmgbpno5E8UMmEitt6gjk8EQEBtSIJl8MLLdQ6Q6n5DYOh7pmy647dmcgJqN1J1-nfydaNjc_h_nsVjsfrLgs1kwayZwmnzSOLc4LqT_boBCwHwvYD78dlk-1FTDp_FblDs7n-lV-UmDkQzx9h6vRe3UJ7ohF-JWol89PdIyfV2Ljm239uB8UMjdUBCG8NNEMsfapEq4BpqQyzRKRGWc1bfnqJuStUCh-LIFmNihE_Bun8ku42Uq5Ctoulxl9cfrYOYPhkKv7sVGJxmF2e1lE296mZHbKepd-nAir6Dlv9riSAgPVUHrYzcXnd5D79HKMJbkVNk4r9PFOdFVnhMnjMAQiIskjJwNwHwwadPu6INYAAVNa6rIxIgJ85HTyciif1teCumvcZ7OE0r2zcNBGUeSfLTJL-WSKKJEbRMrJsJ7QUA3iII5lC9Nu-qANV01OwUZ7Nna3OaP-ShmvcpEPh5vWA44g9EcDUkOLHzpjm4uhWcH9pHEdRE_AM7p1tWc4opvnvTYEDVhSoIlsnwiJtJCYSdKrNP1hD9TuSh3JV8WxOJ8RE02tIqFU8Y2B2UhHnU7bgMXT5NoPDijsNtcC0UY2Kz8gfEo4gLGyKz0ynN2pIqpaxJzW1oehfKpTVi85CfQkYKxwKRPf1APSMD44mT13SQGbUf3VnxNaUUD7bz4eLG0spWBXkE1QBolydCMSZMTOfTzPncVbmebuxsvh6Oc_ZF2-K1KDuM1wWNtYdlYGxRRJHiQGILEc_5e1umDe3b9uokeBMJolNlvaKJAkN6Pu-6m-fRWiqXzshSXtqlqGnO4Srfcl9fIH4BGHYTgObjzR2KDLDiQl0M-CyK97APT75i9f_IizsPPWg60iceQzKzIwR7QfD5f_LYe8aAYGP7ERQSvQCnw1BTF7KBitd07z9RKM2WNu3Jl2elAnYTLeJrPANzNeoTjtLUs1gTXv6cjEdcF4mMS0pWBWf7YQbvDsiZmOnzvp-DKD_Mu2sUmWdsaZwR_694io7VtipcwCzFONpUr6kUvnfvSEpWXGAjTp9KJLdx3dHttkRcELzloM6Q9Y0qi-ximR7jHtyvda6Kw3wpA8T8QSBHRtwUTxYkIuNhRO-EOYQI_kBuucIsqflgwcKg1OSA11tdAwRtSIVkqNM3o5SGyv_7-jZE2UYd6NUBgeW9UgqV5k20VWEnVUjarVjlb2_pDHDTTTo12TKYeRWhg6Nce0wXdKMueLJ-VyL3tpXDSjAyPPCsv2q502N1rkLoL1YX5czxnUPkmCAY7sFEK5kjqljYjdtrEeL5xC0WilP1i9poP5OMU0rkLUdpPT2oYw_qoYnqHcBGbYkaLjgkHKp42lvmqtP68NPVK9EA-4qhzd0YGrFjE_VkrlTQ3Y-z_52_Oo6BO3qgXuCwoX1HuZaSwqMVOE8MfPb_QpPjxxXUrbrm2aeJwAbEt8xi7viy3QtYowu_fatI38h4p5G-bVKBEcRXP0cRnorWsBXVOomyz4uhP-dBQOJZGRgw9cP3sNYW0la-3SoQr-Tq9GdYizLrolbyXc=', 1, '2026-05-20 14:38:23');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `user_chat`
--

CREATE TABLE `user_chat` (
  `dni` varchar(20) NOT NULL,
  `id_chat` int(11) NOT NULL,
  `joined_at` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

--
-- Volcado de datos para la tabla `user_chat`
--

INSERT INTO `user_chat` (`dni`, `id_chat`, `joined_at`) VALUES
('12345678p', 2, '2026-05-20 14:45:21'),
('12345678p', 3, '2026-05-20 14:45:26'),
('12345678p', 4, '2026-05-20 14:46:06'),
('12345678X', 2, '2026-05-20 14:45:21'),
('12345678X', 3, '2026-05-20 14:45:26'),
('12345678X', 4, '2026-05-20 14:46:06');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `user_hierarchy`
--

CREATE TABLE `user_hierarchy` (
  `superior_dni` varchar(20) NOT NULL,
  `subordinate_dni` varchar(20) NOT NULL,
  `assigned_at` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `user_sensor`
--

CREATE TABLE `user_sensor` (
  `dni` varchar(20) NOT NULL,
  `id_sensor` int(11) NOT NULL,
  `assigned_at` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `wind`
--

CREATE TABLE `wind` (
  `id_measurement` int(11) NOT NULL,
  `speed` float NOT NULL,
  `direction` varchar(10) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `zone`
--

CREATE TABLE `zone` (
  `id_zone` int(11) NOT NULL,
  `name` varchar(100) NOT NULL,
  `map_image` longblob DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

--
-- Volcado de datos para la tabla `zone`
--

INSERT INTO `zone` (`id_zone`, `name`, `map_image`) VALUES
(1, 'Main Zone', NULL);

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `air_quality`
--
ALTER TABLE `air_quality`
  ADD PRIMARY KEY (`id_measurement`);

--
-- Indices de la tabla `chat`
--
ALTER TABLE `chat`
  ADD PRIMARY KEY (`id_chat`);

--
-- Indices de la tabla `door_control`
--
ALTER TABLE `door_control`
  ADD PRIMARY KEY (`id_measurement`),
  ADD KEY `user_dni` (`user_dni`);

--
-- Indices de la tabla `humidity`
--
ALTER TABLE `humidity`
  ADD PRIMARY KEY (`id_measurement`);

--
-- Indices de la tabla `lighting`
--
ALTER TABLE `lighting`
  ADD PRIMARY KEY (`id_measurement`);

--
-- Indices de la tabla `measurement`
--
ALTER TABLE `measurement`
  ADD PRIMARY KEY (`id_measurement`),
  ADD KEY `id_sensor` (`id_sensor`);

--
-- Indices de la tabla `message`
--
ALTER TABLE `message`
  ADD PRIMARY KEY (`id_message`),
  ADD KEY `id_chat` (`id_chat`),
  ADD KEY `sender_dni` (`sender_dni`);

--
-- Indices de la tabla `permission`
--
ALTER TABLE `permission`
  ADD PRIMARY KEY (`id_permission`),
  ADD UNIQUE KEY `description` (`description`);

--
-- Indices de la tabla `role`
--
ALTER TABLE `role`
  ADD PRIMARY KEY (`id_role`),
  ADD UNIQUE KEY `role` (`role`);

--
-- Indices de la tabla `role_permission`
--
ALTER TABLE `role_permission`
  ADD PRIMARY KEY (`id_role`,`id_permission`),
  ADD KEY `id_permission` (`id_permission`);

--
-- Indices de la tabla `sensor`
--
ALTER TABLE `sensor`
  ADD PRIMARY KEY (`id_sensor`),
  ADD UNIQUE KEY `name` (`name`),
  ADD KEY `id_zone` (`id_zone`),
  ADD KEY `id_type` (`id_type`),
  ADD KEY `id_role` (`id_role`);

--
-- Indices de la tabla `sensor_ordinario`
--
ALTER TABLE `sensor_ordinario`
  ADD PRIMARY KEY (`id_measurement`);

--
-- Indices de la tabla `temperature`
--
ALTER TABLE `temperature`
  ADD PRIMARY KEY (`id_measurement`);

--
-- Indices de la tabla `ticket`
--
ALTER TABLE `ticket`
  ADD PRIMARY KEY (`id_ticket`),
  ADD KEY `user_dni` (`user_dni`);

--
-- Indices de la tabla `type`
--
ALTER TABLE `type`
  ADD PRIMARY KEY (`id_type`),
  ADD UNIQUE KEY `description` (`description`);

--
-- Indices de la tabla `user`
--
ALTER TABLE `user`
  ADD PRIMARY KEY (`dni`),
  ADD UNIQUE KEY `username` (`username`),
  ADD KEY `id_role` (`id_role`);

--
-- Indices de la tabla `user_chat`
--
ALTER TABLE `user_chat`
  ADD PRIMARY KEY (`dni`,`id_chat`),
  ADD KEY `id_chat` (`id_chat`);

--
-- Indices de la tabla `user_hierarchy`
--
ALTER TABLE `user_hierarchy`
  ADD PRIMARY KEY (`superior_dni`,`subordinate_dni`),
  ADD KEY `subordinate_dni` (`subordinate_dni`);

--
-- Indices de la tabla `user_sensor`
--
ALTER TABLE `user_sensor`
  ADD PRIMARY KEY (`dni`,`id_sensor`),
  ADD KEY `id_sensor` (`id_sensor`);

--
-- Indices de la tabla `wind`
--
ALTER TABLE `wind`
  ADD PRIMARY KEY (`id_measurement`);

--
-- Indices de la tabla `zone`
--
ALTER TABLE `zone`
  ADD PRIMARY KEY (`id_zone`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `chat`
--
ALTER TABLE `chat`
  MODIFY `id_chat` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT de la tabla `measurement`
--
ALTER TABLE `measurement`
  MODIFY `id_measurement` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT de la tabla `message`
--
ALTER TABLE `message`
  MODIFY `id_message` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `permission`
--
ALTER TABLE `permission`
  MODIFY `id_permission` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=10;

--
-- AUTO_INCREMENT de la tabla `role`
--
ALTER TABLE `role`
  MODIFY `id_role` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT de la tabla `sensor`
--
ALTER TABLE `sensor`
  MODIFY `id_sensor` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `ticket`
--
ALTER TABLE `ticket`
  MODIFY `id_ticket` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `type`
--
ALTER TABLE `type`
  MODIFY `id_type` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;

--
-- AUTO_INCREMENT de la tabla `zone`
--
ALTER TABLE `zone`
  MODIFY `id_zone` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- Restricciones para tablas volcadas
--

--
-- Filtros para la tabla `air_quality`
--
ALTER TABLE `air_quality`
  ADD CONSTRAINT `1` FOREIGN KEY (`id_measurement`) REFERENCES `measurement` (`id_measurement`) ON DELETE CASCADE;

--
-- Filtros para la tabla `door_control`
--
ALTER TABLE `door_control`
  ADD CONSTRAINT `1` FOREIGN KEY (`id_measurement`) REFERENCES `measurement` (`id_measurement`) ON DELETE CASCADE,
  ADD CONSTRAINT `2` FOREIGN KEY (`user_dni`) REFERENCES `user` (`dni`) ON UPDATE CASCADE;

--
-- Filtros para la tabla `humidity`
--
ALTER TABLE `humidity`
  ADD CONSTRAINT `1` FOREIGN KEY (`id_measurement`) REFERENCES `measurement` (`id_measurement`) ON DELETE CASCADE;

--
-- Filtros para la tabla `lighting`
--
ALTER TABLE `lighting`
  ADD CONSTRAINT `1` FOREIGN KEY (`id_measurement`) REFERENCES `measurement` (`id_measurement`) ON DELETE CASCADE;

--
-- Filtros para la tabla `measurement`
--
ALTER TABLE `measurement`
  ADD CONSTRAINT `1` FOREIGN KEY (`id_sensor`) REFERENCES `sensor` (`id_sensor`) ON DELETE CASCADE;

--
-- Filtros para la tabla `message`
--
ALTER TABLE `message`
  ADD CONSTRAINT `1` FOREIGN KEY (`id_chat`) REFERENCES `chat` (`id_chat`) ON DELETE CASCADE,
  ADD CONSTRAINT `2` FOREIGN KEY (`sender_dni`) REFERENCES `user` (`dni`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Filtros para la tabla `role_permission`
--
ALTER TABLE `role_permission`
  ADD CONSTRAINT `1` FOREIGN KEY (`id_role`) REFERENCES `role` (`id_role`) ON DELETE CASCADE,
  ADD CONSTRAINT `2` FOREIGN KEY (`id_permission`) REFERENCES `permission` (`id_permission`) ON DELETE CASCADE;

--
-- Filtros para la tabla `sensor`
--
ALTER TABLE `sensor`
  ADD CONSTRAINT `1` FOREIGN KEY (`id_zone`) REFERENCES `zone` (`id_zone`),
  ADD CONSTRAINT `2` FOREIGN KEY (`id_type`) REFERENCES `type` (`id_type`),
  ADD CONSTRAINT `3` FOREIGN KEY (`id_role`) REFERENCES `role` (`id_role`);

--
-- Filtros para la tabla `sensor_ordinario`
--
ALTER TABLE `sensor_ordinario`
  ADD CONSTRAINT `fk_sensor_ordinario_measurement` FOREIGN KEY (`id_measurement`) REFERENCES `measurement` (`id_measurement`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Filtros para la tabla `temperature`
--
ALTER TABLE `temperature`
  ADD CONSTRAINT `1` FOREIGN KEY (`id_measurement`) REFERENCES `measurement` (`id_measurement`) ON DELETE CASCADE;

--
-- Filtros para la tabla `ticket`
--
ALTER TABLE `ticket`
  ADD CONSTRAINT `1` FOREIGN KEY (`user_dni`) REFERENCES `user` (`dni`) ON UPDATE CASCADE;

--
-- Filtros para la tabla `user`
--
ALTER TABLE `user`
  ADD CONSTRAINT `1` FOREIGN KEY (`id_role`) REFERENCES `role` (`id_role`);

--
-- Filtros para la tabla `user_chat`
--
ALTER TABLE `user_chat`
  ADD CONSTRAINT `1` FOREIGN KEY (`dni`) REFERENCES `user` (`dni`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `2` FOREIGN KEY (`id_chat`) REFERENCES `chat` (`id_chat`) ON DELETE CASCADE;

--
-- Filtros para la tabla `user_hierarchy`
--
ALTER TABLE `user_hierarchy`
  ADD CONSTRAINT `1` FOREIGN KEY (`superior_dni`) REFERENCES `user` (`dni`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `2` FOREIGN KEY (`subordinate_dni`) REFERENCES `user` (`dni`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Filtros para la tabla `user_sensor`
--
ALTER TABLE `user_sensor`
  ADD CONSTRAINT `1` FOREIGN KEY (`dni`) REFERENCES `user` (`dni`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `2` FOREIGN KEY (`id_sensor`) REFERENCES `sensor` (`id_sensor`) ON DELETE CASCADE;

--
-- Filtros para la tabla `wind`
--
ALTER TABLE `wind`
  ADD CONSTRAINT `1` FOREIGN KEY (`id_measurement`) REFERENCES `measurement` (`id_measurement`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
