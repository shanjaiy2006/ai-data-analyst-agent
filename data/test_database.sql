CREATE TABLE customers (
    customer_id INT PRIMARY KEY,
    customer_name VARCHAR(100),
    city VARCHAR(100)
);

CREATE TABLE orders (
    order_id INT PRIMARY KEY,
    customer_id INT,
    order_date DATE,
    amount DECIMAL(10,2),
    FOREIGN KEY (customer_id)
        REFERENCES customers(customer_id)
);

INSERT INTO customers
(customer_id, customer_name, city)
VALUES
(1, 'Arun', 'Chennai'),
(2, 'Priya', 'Bangalore'),
(3, 'Rahul', 'Mumbai'),
(4, 'Sneha', 'Chennai');

INSERT INTO orders
(order_id, customer_id, order_date, amount)
VALUES
(101, 1, '2026-01-10', 15000),
(102, 2, '2026-01-12', 22000),
(103, 1, '2026-02-05', 18000),
(104, 3, '2026-02-15', 12000),
(105, 4, '2026-03-01', 30000),
(106, 2, '2026-03-10', 25000);