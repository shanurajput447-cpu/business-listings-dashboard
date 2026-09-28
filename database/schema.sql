CREATE DATABASE IF NOT EXISTS business_listings;
USE business_listings;

CREATE TABLE IF NOT EXISTS listing_master (
    id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    business_name VARCHAR(255) NOT NULL,
    category VARCHAR(150) NULL,
    city VARCHAR(100) NULL,
    address TEXT NULL,
    phone VARCHAR(30) NULL,
    source VARCHAR(100) NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    INDEX idx_listing_master_city (city),
    INDEX idx_listing_master_category (category),
    INDEX idx_listing_master_source (source)
);
