--------------------------------------- Calculate rating trigger
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
  ratingsum FLOAT;
  countsum FLOAT;
  avgnum FLOAT;
BEGIN
  SELECT SUM(R.rating), COUNT(*) INTO ratingsum, countsum
  FROM reviews R
  WHERE R.ccontact = NEW.ccontact;

  SELECT CAST((ratingsum / countsum) AS FLOAT) INTO avgnum;
  UPDATE canparttime  SET avgrating = avgnum
    WHERE ccontact = NEW.ccontact;

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

--------------------------------------- End of calculate rating trigger

--------------------------------------------- Salary trigger

CREATE OR REPLACE FUNCTION 
calcMoney(start DATE, endy DATE, price INTEGER) 
RETURNS INTEGER AS $$
    BEGIN RETURN price * (endy - start);
    END; $$
LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION addSalary()
RETURNS TRIGGER AS $$
BEGIN 
  UPDATE canparttime cp SET salary = salary + 
  (
    SELECT calcMoney(NEW.startday, NEW.endday, 
      (SELECT price FROM dailyprice WHERE
       category = (SELECT category FROM pets P
       WHERE NEW.petname = P.petname AND NEW.pcontact = P.pcontact)
       AND
       rating = (SELECT CEIL(avgrating) FROM canparttime cpt
       WHERE NEW.ccontact = cpt.ccontact)
      )
     )
  )
  WHERE NEW.ccontact = cp.ccontact;
  RETURN NULL;
END;
$$
LANGUAGE PLPGSQL;

DROP TRIGGER IF EXISTS 
newSuccessBidding ON biddings;
CREATE TRIGGER newSuccessBidding
    AFTER UPDATE OF status ON biddings
    FOR EACH ROW
      WHEN (NEW.status = 'success')
        EXECUTE FUNCTION addSalary();
--------------------------------------------- End of salary trigger
---------------------------------- Bid end trigger
CREATE OR REPLACE FUNCTION moveToReview()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO Reviews VALUES (
        NEW.pcontact, NEW.ccontact, NEW.petname,
        NEW.startday, NEW.endday, 5.0, '');
  DELETE FROM biddings WHERE pcontact = NEW.pcontact and ccontact = NEW.ccontact and petname = NEW.petname
    and startday = NEW.startday and endday = NEW.endday;
  RETURN NULL;
END;
$$
LANGUAGE PLPGSQL;


DROP TRIGGER IF EXISTS 
finishedBidding ON biddings;
CREATE TRIGGER finishedBidding
    AFTER UPDATE OF status ON biddings
    FOR EACH ROW
      WHEN (NEW.status = 'end')
        EXECUTE FUNCTION moveToReview();
---------------------------------- End of bid end trigger