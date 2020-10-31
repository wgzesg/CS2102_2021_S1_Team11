CREATE OR REPLACE FUNCTION log_new_successful_bidding()
  RETURNS TRIGGER 
  LANGUAGE PLPGSQL
  AS
$$
BEGIN
	IF NEW.status <> OLD.status  AND NEW.status = 'success' THEN
		 INSERT INTO employee_audits(employee_id,last_name,changed_on)
		 VALUES(OLD.id,OLD.last_name,now());
	END IF;

	RETURN NEW;
END;
$$


CREATE OR REPLACE FUNCTION calculate_avg_rating() 
RETURNS TRIGGER AS $$
DECLARE
  ratingsum INTEGER;
  countsum INTEGER;
  avgnum INTEGER;
BEGIN
  SELECT SUM(R.rating), COUNT(*) INTO ratingsum, countsum
  FROM reviews R
  WHERE R.ccontact = NEW.ccontact;

  SELECT CEILING(ratingsum / countsum) INTO avgnum;
  UPDATE canparttime C SET C.avgrating = avgnum
    WHERE C.ccontact = NEW.ccontact;

  RETURN NULL;

END;
$$ LANGUAGE PLPGSQL;



DROP TRIGGER IF EXISTS
calculate_avg_rating_trigger ON reviews;
CREATE TRIGGER calculate_avg_rating_trigger
  AFTER UPDATE OF rating OR INSERT
  ON reviews
  FOR EACH ROW
  EXECUTE FUNCTION calculate_avg_rating();