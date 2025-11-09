package com.dheeraj.systemanomalymonitor;

import javafx.animation.KeyFrame;
import javafx.animation.Timeline;
import javafx.fxml.FXML;
import javafx.scene.control.Label;
import javafx.util.Duration;
import java.lang.management.ManagementFactory;
import com.sun.management.OperatingSystemMXBean;
import java.util.Map;

public class DashboardController {

    @FXML private Label cpuLabel;
    @FXML private Label ramLabel;
    @FXML private Label diskLabel;
    @FXML private Label netLabel;
    @FXML private Label procLabel;
    @FXML private Label statusLabel;
    @FXML private Label alertSourceLabel;

    private double prevRead = 0, prevWrite = 0, prevSent = 0, prevRecv = 0;

    public void initialize() {
        Timeline timeline = new Timeline(new KeyFrame(Duration.seconds(2), e -> updateMetrics()));
        timeline.setCycleCount(Timeline.INDEFINITE);
        timeline.play();
    }

    private void updateMetrics() {
        try {
            // --- Get base system metrics ---
            OperatingSystemMXBean os = (OperatingSystemMXBean) ManagementFactory.getOperatingSystemMXBean();
            double cpu = os.getSystemCpuLoad() * 100;
            double usedMem = (os.getTotalPhysicalMemorySize() - os.getFreePhysicalMemorySize()) / (1024.0 * 1024 * 1024);
            double totalMem = os.getTotalPhysicalMemorySize() / (1024.0 * 1024 * 1024);
            double ram = (usedMem / totalMem) * 100;

            // --- Disk & Network Stats (quick estimate) ---
            long currRead = os.getCommittedVirtualMemorySize(); // placeholder
            double diskRead = (currRead - prevRead) / (1024.0 * 1024);
            prevRead = currRead;

            double netSent = Math.random() * 100; // placeholder for now
            double netRecv = Math.random() * 100; // placeholder for now
            double procCount = Math.random() * 300; // simulated for demo

            // --- Update labels ---
            cpuLabel.setText(String.format("CPU: %.1f%%", cpu));
            ramLabel.setText(String.format("RAM: %.1f%% (%.2f / %.2f GB)", ram, usedMem, totalMem));
            diskLabel.setText(String.format("Disk: %.2f MB/s", diskRead));
            netLabel.setText(String.format("Network: ↑%.1fKB/s ↓%.1fKB/s", netSent, netRecv));
            procLabel.setText(String.format("Processes: %.0f", procCount));

            // --- Call Python model via bridge ---
            Map<String, Object> result = AnomalyBridge.runModel();
            boolean anomaly = Boolean.TRUE.equals(result.get("anomaly"));
            boolean mlFlag = Boolean.TRUE.equals(result.get("ml_flag"));

            // --- Update UI colors & messages ---
            if (anomaly) {
                statusLabel.setText("⚠️ Anomaly Detected");
                statusLabel.setStyle("-fx-text-fill: red; -fx-font-weight: bold;");
                alertSourceLabel.setText(mlFlag ? "Alert Source: ML Model" : "Alert Source: Statistical Baseline");
            } else {
                statusLabel.setText("✅ Normal");
                statusLabel.setStyle("-fx-text-fill: green; -fx-font-weight: bold;");
                alertSourceLabel.setText("Alert Source: --");
            }

        } catch (Exception ex) {
            statusLabel.setText("⚠️ Error: " + ex.getMessage());
            statusLabel.setStyle("-fx-text-fill: orange;");
            alertSourceLabel.setText("Alert Source: --");
        }
    }
}
