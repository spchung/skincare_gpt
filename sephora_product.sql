-- -------------------------------------------------------------
-- TablePlus 5.3.8(500)
--
-- https://tableplus.com/
--
-- Database: portfolio
-- Generation Time: 2025-05-09 21:26:27.0250
-- -------------------------------------------------------------


-- This script only contains the table creation statements and does not fully represent the table in the database. It's still missing: indices, triggers. Do not use it as a backup.

-- Table Definition
CREATE TABLE "public"."sephora_product" (
    "product_id" varchar NOT NULL,
    "product_name" varchar NOT NULL,
    "brand_id" int4 NOT NULL,
    "brand_name" varchar NOT NULL,
    "loves_count" int4,
    "rating" float8,
    "reviews" int4,
    "size" varchar,
    "ingredients" json,
    "price_usd" float8 NOT NULL,
    "highlights" json,
    "primary_category" varchar NOT NULL,
    "secondary_category" varchar,
    "teritary_category" varchar,
    PRIMARY KEY ("product_id")
);

