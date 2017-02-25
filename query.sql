CREATE TABLE "tag" (
    "tag_id" SERIAL NOT NULL,
    "tag_value" varchar(50) NOT NULL,
    "tag_created" timestamp default CURRENT_TIMESTAMP,
    "tag_updated" timestamp default CURRENT_TIMESTAMP,
    PRIMARY KEY(tag_id)
);

CREATE TABLE "article__tag" (
    "article_id" INTEGER NOT NULL,
    "tag_id" INTEGER NOT NULL,
    PRIMARY KEY ("article_id", "tag_id")
);

CREATE TABLE "category" (
    "category_id" SERIAL NOT NULL,
    "category_title" varchar(50) NOT NULL,
    "category_created" timestamp default CURRENT_TIMESTAMP,
    "category_updated" timestamp default CURRENT_TIMESTAMP,
    PRIMARY KEY(category_id)
);

CREATE TABLE "article" (
    "article_id" SERIAL NOT NULL,
    "article_text" text NOT NULL,
		"article_title" varchar(50) NOT NULL,
    "article_created" timestamp default CURRENT_TIMESTAMP,
    "article_updated" timestamp default CURRENT_TIMESTAMP,
    PRIMARY KEY(article_id)
);

ALTER TABLE "article" ADD "category_id" integer NOT NULL,
    ADD CONSTRAINT "fk_article_category_id" FOREIGN KEY ("category_id")
    REFERENCES "category" ("category_id");

ALTER TABLE "article__tag" ADD CONSTRAINT "fk_articletag_article_id" FOREIGN KEY ("article_id")
    REFERENCES "article" ("article_id");

ALTER TABLE "article__tag" ADD CONSTRAINT "fk_articletag_tag_id" FOREIGN KEY ("tag_id")
    REFERENCES "tag" ("tag_id");

CREATE OR REPLACE FUNCTION update_time()
RETURNS TRIGGER AS $$
BEGIN
    NEW.article_updated = now();
    RETURN NEW;
END;
$$ language 'plpgsql';
CREATE TRIGGER update_time BEFORE UPDATE ON "article" FOR EACH ROW EXECUTE PROCEDURE update_time();

CREATE OR REPLACE FUNCTION update_time()
RETURNS TRIGGER AS $$
BEGIN
    NEW.category_updated = now();
    RETURN NEW;
END;
$$ language 'plpgsql';
CREATE TRIGGER update_time BEFORE UPDATE ON "category" FOR EACH ROW EXECUTE PROCEDURE update_time();

CREATE OR REPLACE FUNCTION update_time()
RETURNS TRIGGER AS $$
BEGIN
    NEW.tag_updated = now();
    RETURN NEW;
END;
$$ language 'plpgsql';
CREATE TRIGGER update_time BEFORE UPDATE ON "tag" FOR EACH ROW EXECUTE PROCEDURE update_time();

