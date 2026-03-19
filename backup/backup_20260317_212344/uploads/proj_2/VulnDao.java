// Java 漏洞样本3

import java.sql.*;
import java.io.*;

public class VulnDao {

    // 硬编码密码（规则6）
    private String password = "DaoLayer@Pass2026";
    private String db_password = "SqlServer#Root";

    // SQL注入（规则4：executeQuery + +号拼接同一行）
    public ResultSet findById(String id) throws Exception {
        Connection conn = DriverManager.getConnection("jdbc:mysql://localhost/erp", "root", "123456");
        return conn.createStatement().executeQuery("SELECT * FROM employee WHERE id=" + id);
    }

    public ResultSet findByDept(String dept) throws Exception {
        Connection conn = DriverManager.getConnection("jdbc:mysql://localhost/erp", "root", "123456");
        return conn.createStatement().executeQuery("SELECT * FROM employee WHERE dept='" + dept + "'");
    }

    public ResultSet searchProduct(String keyword) throws Exception {
        Connection conn = DriverManager.getConnection("jdbc:mysql://localhost/shop", "root", "123456");
        return conn.createStatement().executeQuery("SELECT * FROM product WHERE name LIKE '%" + keyword + "%'");
    }

    public ResultSet getReport(String month) throws Exception {
        Connection conn = DriverManager.getConnection("jdbc:mysql://localhost/report", "root", "123456");
        return conn.createStatement().executeQuery("SELECT * FROM monthly WHERE month='" + month + "'");
    }

    // Java反序列化（规则10）
    public static Object deserializeToken(byte[] token) throws Exception {
        ObjectInputStream ois = new ObjectInputStream(new ByteArrayInputStream(token));
        return ois.readObject();
    }

    public static Object readFromFile(String path) throws Exception {
        ObjectInputStream ois = new ObjectInputStream(new FileInputStream(path));
        return ois.readObject();
    }

    // 路径穿越（规则7）
    public String readFile(String name) throws Exception {
        return new String(new FileInputStream("/data/files/../../../" + name).readAllBytes());
    }
}

