package com.dheeraj.systemanomalymonitor;

import java.io.*;
import java.net.Socket;
import java.util.HashMap;
import java.util.Map;
import com.fasterxml.jackson.databind.ObjectMapper;

public class AnomalyBridge {

    private static final String HOST = "127.0.0.1";
    private static final int PORT = 5055;
    private static final ObjectMapper mapper = new ObjectMapper();

    public static Map<String, Object> runModel() {
        Map<String, Object> result = new HashMap<>();

        try (Socket socket = new Socket(HOST, PORT)) {
            OutputStream out = socket.getOutputStream();
            out.write("ping\n".getBytes());
            out.flush();

            BufferedReader in = new BufferedReader(new InputStreamReader(socket.getInputStream()));
            StringBuilder sb = new StringBuilder();
            String line;
            while ((line = in.readLine()) != null) sb.append(line);

            String output = sb.toString().trim();
            System.out.println("📡 Raw server output: " + output);

            Map<String, Object> parsed = mapper.readValue(output, Map.class);

            result.putAll(parsed);

        } catch (Exception e) {
            result.put("error", e.getMessage());
        }
        return result;
    }

}
