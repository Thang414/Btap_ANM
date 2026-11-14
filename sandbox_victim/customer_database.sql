-- Database Dump: Customer Information 2026
CREATE TABLE customers (
    id INT PRIMARY KEY AUTO_INCREMENT,
    full_name VARCHAR(100),
    email VARCHAR(100),
    card_token VARCHAR(64),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO customers (full_name, email, card_token) VALUES
('Nguyen Van An', 'an.nguyen@corporation.vn', 'tok_visa_89234872138'),
('Tran Thi Binh', 'binh.tran@techgroup.vn', 'tok_mc_98374928173'),
('Le Hoang Minh', 'minh.le@vietsecurity.edu.vn', 'tok_jcb_12938172938');
