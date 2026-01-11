package com.dheeraj.systemanomalymonitor;

import javafx.animation.PauseTransition;
import javafx.fxml.FXML;
import javafx.scene.control.*;
import javafx.util.Duration;
import java.io.*;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.Map;

public class DashboardController {

    @FXML private Label cpuLabel;
    @FXML private Label ramLabel;
    @FXML private Label diskLabel;
    @FXML private Label netLabel;
    @FXML private Label procLabel;
    @FXML private Label statusLabel;
    @FXML private Label hintLabel;
    @FXML private Button trueButton;
    @FXML private Button falseButton;

    private Map<String, Object> lastMetrics;
    private final File feedbackFile;
    private boolean feedbackActive = false;
    private PauseTransition feedbackTimer;
    private boolean feedbackSubmitted = false;



    public DashboardController() {
        feedbackFile = new File("src/main/python/feedback_log.csv");
        try {
            if (!feedbackFile.exists()) {
                feedbackFile.getParentFile().mkdirs();
                try (FileWriter w = new FileWriter(feedbackFile, true)) {
                    w.write("timestamp,cpu,ram,disk_read,disk_write,net_sent,net_recv,proc,predicted_anomaly,user_label\n");
                }
            }
        } catch (IOException e) {
            System.err.println("⚠️ Could not create feedback file: " + e.getMessage());
        }
    }

    public void updateMetrics(Map<String, Object> metrics) {
        this.lastMetrics = metrics;

        double cpu = ((Number) metrics.getOrDefault("cpu", 0)).doubleValue();
        double ram = ((Number) metrics.getOrDefault("ram", 0)).doubleValue();
        double diskR = ((Number) metrics.getOrDefault("disk_read", 0)).doubleValue();
        double diskW = ((Number) metrics.getOrDefault("disk_write", 0)).doubleValue();
        double netS = ((Number) metrics.getOrDefault("net_sent", 0)).doubleValue();
        double netR = ((Number) metrics.getOrDefault("net_recv", 0)).doubleValue();
        int proc = ((Number) metrics.getOrDefault("proc", 0)).intValue();
        boolean anomaly = (Boolean) metrics.getOrDefault("anomaly", false);

        cpuLabel.setText(String.format("CPU Usage: %.1f%%", cpu));
        ramLabel.setText(String.format("Memory Used: %.1f%%", ram));
        diskLabel.setText(String.format("Disk Read/Write: %.1f / %.1f MB/s", diskR, diskW));
        netLabel.setText(String.format("Network Sent/Recv: %.1f / %.1f KB/s", netS, netR));
        procLabel.setText(String.format("Process Count: %d", proc));

        if (anomaly && !feedbackSubmitted) {
            statusLabel.setText("🚨 Anomaly Detected!");
            statusLabel.setStyle("-fx-text-fill: red; -fx-font-weight: bold;");
            enableFeedbackButtons();
        } else {
            statusLabel.setText("✅ Normal");
            statusLabel.setStyle("-fx-text-fill: green;");
            disableFeedbackButtons();
        }

    }

    private void enableFeedbackButtons() {
        feedbackSubmitted = false; // reset ONLY once per anomaly

        trueButton.setDisable(false);
        falseButton.setDisable(false);

        trueButton.setStyle("-fx-background-color: #28a745; -fx-text-fill: white;");
        falseButton.setStyle("-fx-background-color: #dc3545; -fx-text-fill: white;");

        if (feedbackTimer != null) {
            feedbackTimer.stop();
        }

        feedbackTimer = new PauseTransition(Duration.seconds(15));
        feedbackTimer.setOnFinished(e -> disableFeedbackButtons());
        feedbackTimer.play();
    }




    @FXML
    private void onTrueAnomaly() {
        if (feedbackSubmitted) return; // 🚫 HARD STOP

        feedbackSubmitted = true;
        logFeedback("TRUE");
        hintLabel.setText("✔️ Logged: TRUE");

        disableFeedbackButtons();
    }

    @FXML
    private void onFalseAlarm() {
        if (feedbackSubmitted) return; // 🚫 HARD STOP

        feedbackSubmitted = true;
        logFeedback("FALSE");
        hintLabel.setText("❌ Logged: FALSE");

        disableFeedbackButtons();
    }


    @FXML private Label connLabel;
    public void setConnectionStatus(boolean connected) {
        if (connected) {
            connLabel.setText("🟢 Connected");
            connLabel.setStyle("-fx-text-fill: green;");
        } else {
            connLabel.setText("🔴 Disconnected");
            connLabel.setStyle("-fx-text-fill: red;");
        }
    }

    private void disableFeedbackButtons() {
        trueButton.setDisable(true);
        falseButton.setDisable(true);
        trueButton.setStyle("");
        falseButton.setStyle("");
    }



    private void logFeedback(String userLabel) {
        if (lastMetrics == null) return;

        double cpu = ((Number) lastMetrics.getOrDefault("cpu", 0)).doubleValue();
        double ram = ((Number) lastMetrics.getOrDefault("ram", 0)).doubleValue();
        double diskR = ((Number) lastMetrics.getOrDefault("disk_read", 0)).doubleValue();
        double diskW = ((Number) lastMetrics.getOrDefault("disk_write", 0)).doubleValue();
        double netS = ((Number) lastMetrics.getOrDefault("net_sent", 0)).doubleValue();
        double netR = ((Number) lastMetrics.getOrDefault("net_recv", 0)).doubleValue();
        int proc = ((Number) lastMetrics.getOrDefault("proc", 0)).intValue();
        boolean predicted = (boolean) lastMetrics.getOrDefault("anomaly", false);

        String ts = LocalDateTime.now().format(DateTimeFormatter.ISO_LOCAL_DATE_TIME);
        String row = String.format("%s,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%d,%b,%s\n",
                ts, cpu, ram, diskR, diskW, netS, netR, proc, predicted, userLabel);

        try (FileWriter fw = new FileWriter(feedbackFile, true)) {
            fw.write(row);
        } catch (IOException e) {
            System.err.println("⚠️ Error writing feedback: " + e.getMessage());
        }

        System.out.println("📘 Logged feedback: " + row.trim());
    }
}
