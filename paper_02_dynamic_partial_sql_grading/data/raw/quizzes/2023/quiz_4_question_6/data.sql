-- SQL script for creating and populating a star schema in PostgreSQL

-- Drop tables if they already exist
DROP TABLE IF EXISTS Fact_Table, Product_DIM, Customer_DIM, Time_DIM, Promotion_DIM CASCADE;

-- Creating dimension tables
CREATE TABLE Product_DIM (
    Product_ID SERIAL PRIMARY KEY,
    Product_Name VARCHAR(255),
    Unit_Price DECIMAL,
    Product_Line VARCHAR(255)
);

CREATE TABLE Customer_DIM (
    Customer_ID SERIAL PRIMARY KEY,
    Name VARCHAR(255),
    City VARCHAR(255),
    Zip VARCHAR(10)
);

CREATE TABLE Time_DIM (
    Time_ID SERIAL PRIMARY KEY,
    Order_Date DATE,
    Month VARCHAR(10),
    Quarter VARCHAR(10),
    Year INT
);

CREATE TABLE Promotion_DIM (
    Promotion_ID SERIAL PRIMARY KEY,
    Promo_Name VARCHAR(255),
    Ad_Type VARCHAR(255),
    Coupon_Type VARCHAR(255),
    Price_Reduction_Type VARCHAR(255)
);

-- Creating the fact table
CREATE TABLE Fact_Table (
    Product_ID INT REFERENCES Product_DIM(Product_ID),
    Time_ID INT REFERENCES Time_DIM(Time_ID),
    Promotion_ID INT REFERENCES Promotion_DIM(Promotion_ID),
    Customer_ID INT REFERENCES Customer_DIM(Customer_ID),
    Revenue DECIMAL,
    Units_Sold INT
);

-- Inserting sample data into dimension tables
INSERT INTO Product_DIM (Product_Name, Unit_Price, Product_Line) VALUES
('Product A', 20.50, 'Electronics'),
('Product B', 15.00, 'Clothing'),
('Product C', 30.00, 'Kitchenware');

INSERT INTO Customer_DIM (Name, City, Zip) VALUES
('John Doe', 'New York', '10001'),
('Jane Smith', 'Los Angeles', '90001'),
('Alice Johnson', 'Chicago', '60601');

INSERT INTO Time_DIM (Order_Date, Month, Quarter, Year) VALUES
('2023-01-15', 'January', 'Q1', 2023),
('2023-02-20', 'February', 'Q1', 2023),
('2023-03-10', 'March', 'Q1', 2023);

INSERT INTO Promotion_DIM (Promo_Name, Ad_Type, Coupon_Type, Price_Reduction_Type) VALUES
('Summer Sale', 'TV', 'Online', 'Percentage'),
('Winter Discount', 'Radio', 'In-Store', 'Fixed Amount'),
('Black Friday', 'Online', 'Both', 'Percentage');

-- Inserting sample data into the fact table
INSERT INTO Fact_Table (Product_ID, Time_ID, Promotion_ID, Customer_ID, Revenue, Units_Sold) VALUES
(1, 1, 1, 1, 100.00, 2),
(2, 2, 2, 2, 150.00, 10),
(3, 3, 3, 3, 450.00, 15);
