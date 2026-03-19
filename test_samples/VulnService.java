// Java 漏洞样本2

import java.sql.*;
import java.io.*;

public class VulnService {

    // 硬编码密码（规则6）
    private static final String password = "JavaAdmin@2026";
    private static final String db_password = "OraclePass#88";
    private static final String redis_password = "RedisAuth!2026";

    // SQL注入（规则4：executeQuery + +号拼接同一行）
    public static ResultSet queryUser(String name) throws Exception {
        Connection conn = DriverManager.getConnection("jdbc:mysql://localhost/app", "root", "123456");
        return conn.createStatement().executeQuery("SELECT * FROM user WHERE name='" + name + "'");
    }

    public static ResultSet queryOrder(String status) throws Exception {
        Connection conn = DriverManager.getConnection("jdbc:mysql://localhost/shop", "root", "123456");
        return conn.createStatement().executeQuery("SELECT * FROM orders WHERE status='" + status + "'");
    }

    public static ResultSet queryLog(String level) throws Exception {
        Connection conn = DriverManager.getConnection("jdbc:mysql://localhost/log", "root", "123456");
        return conn.createStatement().executeQuery("SELECT * FROM syslog WHERE level='" + level + "'");
    }

    // Java反序列化（规则10）
    public static Object loadSession(byte[] data) throws Exception {
        ObjectInputStream ois = new ObjectInputStream(new ByteArrayInputStream(data));
        return ois.readObject();
    }

    public static Object loadCache(InputStream input) throws Exception {
        ObjectInputStream ois = new ObjectInputStream(input);
        return ois.readObject();
    }

    // 路径穿越（规则7）
    public static String readConfig(String name) throws Exception {
        return new BufferedReader(new FileReader("/opt/app/config/../../../etc/" + name)).readLine();
    }

    public static byte[] readUpload(String filename) throws Exception {
        return new FileInputStream("/var/uploads/../../../tmp/" + filename).readAllBytes();
    }
}

