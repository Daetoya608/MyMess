CREATE TABLE message_log (
    id SERIAL PRIMARY KEY,
    message_id INTEGER,
    sender_id INTEGER,
    chat_id INTEGER,
    log_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE OR REPLACE FUNCTION log_new_message()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO message_log (message_id, sender_id, chat_id)
    VALUES (NEW.id, NEW.sender_id, NEW.chat_id);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;


CREATE TRIGGER trg_log_message
AFTER INSERT ON message
FOR EACH ROW
EXECUTE FUNCTION log_new_message();


CREATE OR REPLACE FUNCTION delete_versions_on_message_delete()
RETURNS TRIGGER AS $$
BEGIN
    DELETE FROM message_version WHERE message_id = OLD.id;
    RETURN OLD;
END;
$$ LANGUAGE plpgsql;


CREATE TRIGGER trg_delete_versions
AFTER DELETE ON message
FOR EACH ROW
EXECUTE FUNCTION delete_versions_on_message_delete();


CREATE OR REPLACE FUNCTION save_message_version()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.content_text IS DISTINCT FROM OLD.content_text THEN
        INSERT INTO message_version(message_id, content_text, valid_from)
        VALUES (OLD.id, OLD.content_text, OLD.created_at);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;


CREATE TRIGGER trg_save_version
BEFORE UPDATE ON message
FOR EACH ROW
EXECUTE FUNCTION save_message_version();
