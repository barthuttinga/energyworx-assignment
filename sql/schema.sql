CREATE TABLE url (
    id INTEGER NOT NULL AUTO_INCREMENT,
    url VARCHAR(255) NOT NULL,
    shortcode VARCHAR(6) NOT NULL,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_redirect TIMESTAMP NULL,
    redirect_count INTEGER DEFAULT 0,
    PRIMARY KEY (id),
    UNIQUE (shortcode)
);
