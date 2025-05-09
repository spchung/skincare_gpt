-- -------------------------------------------------------------
-- TablePlus 5.3.8(500)
--
-- https://tableplus.com/
--
-- Database: portfolio
-- Generation Time: 2025-05-09 21:26:46.8060
-- -------------------------------------------------------------


-- This script only contains the table creation statements and does not fully represent the table in the database. It's still missing: indices, triggers. Do not use it as a backup.

-- Table Definition
CREATE TABLE "public"."sephora_review" (
    "review_id" varchar NOT NULL,
    "author_id" varchar NOT NULL,
    "rating" int4 NOT NULL,
    "is_recommended" bool NOT NULL,
    "helpfulness" float8,
    "total_feedback_count" int4 NOT NULL,
    "total_neg_feedback_count" int4 NOT NULL,
    "total_pos_feedback_count" int4 NOT NULL,
    "submission_time" varchar NOT NULL,
    "review_text" varchar NOT NULL,
    "review_title" varchar NOT NULL,
    "skin_tone" varchar,
    "eye_color" varchar,
    "skin_type" varchar,
    "hair_color" varchar,
    "product_id" varchar NOT NULL,
    "product_name" varchar NOT NULL,
    "brand_name" varchar NOT NULL,
    "price_usd" float8 NOT NULL,
    PRIMARY KEY ("review_id")
);

