// Java 测试样本 - 包含多种安全漏洞（仅用于审计工具测试）

import java.sql.*;
import java.io.*;

public class TestVulns {

    // ===== 1. SQL 注入（规则4：同一行有 executeQuery 且有 + 号拼接） =====
    public static void getUserById(String userId) throws Exception {
        Connection conn = DriverManager.getConnection("jdbc:mysql://localhost/test", "root", "123456");
        Statement stmt = conn.createStatement();
        ResultSet rs = stmt.executeQuery("SELECT * FROM user WHERE id = " + userId);  // 漏洞
        while (rs.next()) {
            System.out.println(rs.getString("name"));
        }
    }

    // ===== 2. Java 反序列化（规则10：直接使用 ObjectInputStream） =====
    public static Object deserialize(byte[] data) throws Exception {
        ObjectInputStream ois = new ObjectInputStream(new ByteArrayInputStream(data));  // 漏洞
        return ois.readObject();
    }

    // ===== 3. 敏感信息硬编码（规则6：password\s*=） =====
    private static final String password = "Root@2026!";        // 漏洞
    private static final String db_password = "Admin#Pass";     // 漏洞

    // ===== 4. 路径穿越（规则7：\.\.\/） =====
    public static String readFile(String filename) throws Exception {
        // 漏洞：路径包含 ../
        FileReader fr = new FileReader("/opt/app/uploads/../../../etc/" + filename);
        return new BufferedReader(fr).readLine();
    }

    // ===== 正常代码（不应触发） =====
    public static void safeQuery(String userId) throws Exception {
        Connection conn = DriverManager.getConnection("jdbc:mysql://localhost/test", "root", "123456");
        PreparedStatement ps = conn.prepareStatement("SELECT * FROM user WHERE id = ?");
        ps.setString(1, userId);
        ps.executeQuery();
    }
}

