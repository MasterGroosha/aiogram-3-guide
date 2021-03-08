BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "youtube" (
	"user_id"	INTEGER NOT NULL,
	"youtube_hash"	TEXT NOT NULL,
	"description"	TEXT NOT NULL,
	PRIMARY KEY("user_id","youtube_hash")
);
COMMIT;
