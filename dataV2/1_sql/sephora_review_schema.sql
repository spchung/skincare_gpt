-- -------------------------------------------------------------
-- TablePlus 5.3.8(500)
--
-- https://tableplus.com/
--
-- Database: skincare_gpt
-- Generation Time: 2025-06-29 12:28:30.3210
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

INSERT INTO "public"."sephora_review" ("review_id", "author_id", "rating", "is_recommended", "helpfulness", "total_feedback_count", "total_neg_feedback_count", "total_pos_feedback_count", "submission_time", "review_text", "review_title", "skin_tone", "eye_color", "skin_type", "hair_color", "product_id", "product_name", "brand_name", "price_usd") VALUES
('0', '1741593524', 5, 't', 1, 2, 0, 2, '2023-02-01', 'I use this with the Nudestix “Citrus Clean Balm & Make-Up Melt“ to double cleanse and it has completely changed my skin (for the better). The make-up melt is oil based and removes all of your makeup super easily. I follow-up with this water based cleanser, and I also use this just by itself when I’m not wearing make-up. It leaves the skin gently cleansed, but without stripping the skin. 10/10 recommend combining with the make-up melt. It’s perfection!', 'Taught me how to double cleanse!', NULL, 'brown', 'dry', 'black', 'P504322', 'Gentle Hydra-Gel Face Cleanser', 'NUDESTIX', 19),
('1', '5478482359', 3, 't', 0.3333329856395721, 3, 2, 1, '2021-12-17', 'I gave this 3 stars because it give me tiny little white heads from first use ima give it few more days before making a final decision on keeping or returning it, all thought it did keep my oily face under control and I was not as oily but it feels though as it trapped the oil in my pores?!', 'it keeps oily skin under control', 'mediumTan', 'brown', 'oily', 'black', 'P379064', 'Lotus Balancing & Hydrating Natural Face Treatment Oil', 'Clarins', 65)