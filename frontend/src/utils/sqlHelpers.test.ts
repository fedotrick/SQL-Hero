import { describe, it, expect } from "vitest";
import { extractTableNames, formatSQL } from "./sqlHelpers";

describe("sqlHelpers", () => {
  describe("extractTableNames", () => {
    it("extracts table names from FROM clause", () => {
      const text = "SELECT * FROM users WHERE id = 1";
      const tables = extractTableNames(text);
      expect(tables).toContain("users");
    });

    it("extracts table names from JOIN clause", () => {
      const text = "SELECT * FROM users JOIN orders ON users.id = orders.user_id";
      const tables = extractTableNames(text);
      expect(tables).toContain("users");
      expect(tables).toContain("orders");
    });

    it("extracts table names from INSERT INTO", () => {
      const text = "INSERT INTO products (name, price) VALUES ('Test', 10)";
      const tables = extractTableNames(text);
      expect(tables).toContain("products");
    });

    it("extracts table names from UPDATE", () => {
      const text = "UPDATE customers SET name = 'John' WHERE id = 1";
      const tables = extractTableNames(text);
      expect(tables).toContain("customers");
    });

    it("extracts table names from CREATE TABLE", () => {
      const text = "CREATE TABLE employees (id INT, name VARCHAR(100))";
      const tables = extractTableNames(text);
      expect(tables).toContain("employees");
    });

    it("extracts table names from Russian text", () => {
      const text = "Используйте таблицу users для получения данных";
      const tables = extractTableNames(text);
      expect(tables).toContain("users");
    });

    it("extracts multiple unique table names", () => {
      const text = `
        SELECT * FROM users 
        JOIN orders ON users.id = orders.user_id
        JOIN products ON orders.product_id = products.id
      `;
      const tables = extractTableNames(text);
      expect(tables).toHaveLength(3);
      expect(tables).toContain("users");
      expect(tables).toContain("orders");
      expect(tables).toContain("products");
    });

    it("returns lowercase table names", () => {
      const text = "SELECT * FROM Users JOIN Orders";
      const tables = extractTableNames(text);
      expect(tables).toContain("users");
      expect(tables).toContain("orders");
    });

    it("handles empty string", () => {
      const tables = extractTableNames("");
      expect(tables).toEqual([]);
    });

    it("removes duplicates", () => {
      const text = "SELECT * FROM users JOIN users ON users.id = users.parent_id";
      const tables = extractTableNames(text);
      expect(tables).toHaveLength(1);
      expect(tables).toContain("users");
    });

    it("handles backtick-quoted table names in Russian text", () => {
      const text = "Работа с таблицей `users` и таблицей `orders`";
      const tables = extractTableNames(text);
      expect(tables).toContain("users");
      expect(tables).toContain("orders");
    });
  });

  describe("formatSQL", () => {
    it("removes extra whitespace", () => {
      const sql = "SELECT   *   FROM    users";
      const formatted = formatSQL(sql);
      expect(formatted).toBe("SELECT * FROM users");
    });

    it("trims leading and trailing whitespace", () => {
      const sql = "  SELECT * FROM users  ";
      const formatted = formatSQL(sql);
      expect(formatted).toBe("SELECT * FROM users");
    });

    it("handles newlines", () => {
      const sql = `SELECT *
      FROM users
      WHERE id = 1`;
      const formatted = formatSQL(sql);
      expect(formatted).toBe("SELECT * FROM users WHERE id = 1");
    });

    it("handles tabs", () => {
      const sql = "SELECT\t*\tFROM\tusers";
      const formatted = formatSQL(sql);
      expect(formatted).toBe("SELECT * FROM users");
    });

    it("handles empty string", () => {
      const formatted = formatSQL("");
      expect(formatted).toBe("");
    });
  });
});
