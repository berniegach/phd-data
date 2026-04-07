-- Drop tables if they exist (optional cleanup)
DROP TABLE IF EXISTS Fact_Table;
DROP TABLE IF EXISTS Product_DIM;
DROP TABLE IF EXISTS Customer_DIM;
DROP TABLE IF EXISTS Time_DIM;
DROP TABLE IF EXISTS Promotion_DIM;

-- Create dimension tables
CREATE TABLE Product_DIM (
    Product_ID INTEGER PRIMARY KEY,
    Product_Name VARCHAR,
    Unit_Price DECIMAL(10,2),
    Product_Line VARCHAR
);

CREATE TABLE Customer_DIM (
    Customer_ID INTEGER PRIMARY KEY,
    Name VARCHAR,
    City VARCHAR,
    Zip VARCHAR
);

CREATE TABLE Time_DIM (
    Time_ID INTEGER PRIMARY KEY,
    Order_Date DATE,
    Month INTEGER,
    Quarter INTEGER,
    Year INTEGER
);

CREATE TABLE Promotion_DIM (
    Promotion_ID INTEGER PRIMARY KEY,
    Promo_Name VARCHAR,
    Ad_Type VARCHAR,
    Coupon_Type VARCHAR,
    Price_Reduction_Type VARCHAR
);

-- Create fact table
CREATE TABLE Fact_Table (
    Product_ID INTEGER,
    Time_ID INTEGER,
    Promotion_ID INTEGER,
    Customer_ID INTEGER,
    Revenue DECIMAL(10,2),
    Units_Sold INTEGER
);

-- Insert data into dimension tables
INSERT INTO Product_DIM VALUES
(1, 'Widget A', 10.00, 'Widgets'),
(2, 'Widget B', 12.50, 'Widgets'),
(3, 'Gadget X', 20.00, 'Gadgets');

INSERT INTO Customer_DIM VALUES
(100, 'Alice', 'Nijmegen', '6500AA'),
(101, 'Bob', 'Amsterdam', '1000AA'),
(102, 'Charlie', 'Rotterdam', '3000BB');

INSERT INTO Time_DIM VALUES
(2021001, '2021-01-15', 1, 1, 2021),
(2021002, '2021-02-10', 2, 1, 2021),
(2020001, '2020-05-10', 5, 2, 2020);

INSERT INTO Promotion_DIM VALUES
(10, 'Christmas Promo', 'Online', 'Coupon', 'Percentage'),
(11, 'Summer Sale', 'TV', 'No Coupon', 'Absolute');

-- Insert data into fact table
-- Matching the conditions: City = 'Nijmegen' and Year = 2021
-- We'll make sure one of these rows involves a customer in Nijmegen (Alice) and a 2021 date (Time_ID=2021001)
INSERT INTO Fact_Table VALUES
(1, 2021001, 10, 100, 500.00, 50),   -- Matches Alice in 2021
(2, 2020001, 11, 101, 300.00, 30),   -- Different city/year, won't match query condition
(3, 2021002, 10, 102, 250.00, 25);   -- 2021 but City is Rotterdam, won't match city condition

-- After running the above, execute the provided query:
-- SELECT Name, SUM(Revenue) 
-- FROM Fact_Table NATURAL JOIN Customer_DIM NATURAL JOIN Time_DIM 
-- WHERE City = 'Nijmegen' AND Year = 2021 
-- GROUP BY Name;
