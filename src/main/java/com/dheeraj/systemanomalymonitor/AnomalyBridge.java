package com.dheeraj.systemanomalymonitor;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.net.Socket;
import java.util.HashMap;
import java.util.Map;

public class AnomalyBridge {

    private static final String HOST = "127.0.0.1";
    private static final int PORT = 5055;

    public static Map<String, Object> runModel() {
        Map<String, Object> result = new HashMap<>();
        try (Socket socket = new Socket(HOST, PORT)) {
            OutputStream out = socket.getOutputStream();
            out.write("ping".getBytes());
            out.flush();

            BufferedReader in = new BufferedReader(new InputStreamReader(socket.getInputStream()));
            StringBuilder sb = new StringBuilder();
            String line;
            while ((line = in.readLine()) != null) sb.append(line);

            String output = sb.toString();
            result.put("raw_output", output);
            result.put("anomaly", output.contains("\"anomaly\": true"));
            result.put("ml_flag", output.contains("\"ml_flag\": true"));

        } catch (Exception e) {
            result.put("error", e.getMessage());
        }
        return result;
    }
}
