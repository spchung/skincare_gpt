-- -------------------------------------------------------------
-- TablePlus 5.3.8(500)
--
-- https://tableplus.com/
--
-- Database: skincare_gpt
-- Generation Time: 2025-06-29 12:28:17.2030
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

INSERT INTO "public"."sephora_product" ("product_id", "product_name", "brand_id", "brand_name", "loves_count", "rating", "reviews", "size", "ingredients", "price_usd", "highlights", "primary_category", "secondary_category", "teritary_category") VALUES
('P114902', 'Goodbye Acne  Max Complexion Correction Pads', 3728, 'Peter Thomas Roth', 56955, 4.4199, 1529, '60 pads', '["Salicylic Acid 2%, Alcohol Denat., Water/Aqua/Eau, Butylene Glycol, Glycolic Acid, Hamamelis Virginiana (Witch Hazel) Water, Aloe Barbadensis Leaf Juice, Arginine, Sodium Hydroxide, Chamomilla Recutita (Matricaria) Flower Extract, Fragrance/Parfum, Prunus Persica (Peach) Fruit Extract, Camellia Sinensis Leaf Extract, Phenoxyethanol, Symphytum Officinale Leaf Extract, Allantoin, Triethanolamine, Amyl Cinnamal, Linalool, Limonene, Benzoic Acid, Geraniol, Butylphenyl Methylpropional, Citronellol, Citric Acid, Potassium Sorbate, Sodium Benzoate, Benzyl Alcohol, Citral, Benzyl Benzoate."]', 48, '["Good for: Pores", "Good for: Acne/Blemishes", "Best for Oily, Combo, Normal Skin", "Without Sulfates SLS & SLES"]', 'Skincare', 'Treatments', NULL),
('P12045', 'Grape Water Moisturizing Face Mist', 4171, 'Caudalie', 140024, 4.4431, 1686, '2.5 oz / 75 mL', '["Vitis Vinifera (Grape) Fruit Water*, Vitis Vinifera (Grape) Juice*, Nitrogen."]', 12, '["Good for: Redness", "Best for Dry Skin", "Clean + Planet Positive", "Hydrating", "Good for: Dryness"]', 'Skincare', 'Moisturizers', NULL)
