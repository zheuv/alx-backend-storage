-- creates a trigger that decreases the quantity

CREATE TRIGGER dec_q AFTER INSERT ON orders FOR EACH ROW
UPDATE items SET quantity = quatity - NEW.number WHERE name = NEW.item_name
