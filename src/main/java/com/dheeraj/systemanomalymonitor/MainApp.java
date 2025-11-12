package com.dheeraj.systemanomalymonitor;

import javafx.animation.KeyFrame;
import javafx.animation.Timeline;
import javafx.application.Application;
import javafx.fxml.FXMLLoader;
import javafx.scene.Parent;
import javafx.scene.Scene;
import javafx.stage.Stage;
import javafx.util.Duration;
import java.lang.management.ManagementFactory;
import com.sun.management.OperatingSystemMXBean;
import java.util.*;
import java.nio.file.*;
import java.io.IOException;

public class MainApp extends Application {
    private DashboardController controller;
    private long lastDiskRead = 0, lastDiskWrite = 0, lastNetSent = 0, lastNetRecv = 0;

    @Override
    public void start(Stage stage) throws Exception {
        FXMLLoader loader = new FXMLLoader(
                MainApp.class.getResource("/com/dheeraj/systemanomalymonitor/dashboard.fxml")
        );
        Parent root = loader.load();
        controller = loader.getController();

        Scene scene = new Scene(root, 500, 360);
        stage.setTitle("System Anomaly Monitor");
        stage.setScene(scene);
        stage.show();

        updateBaseline();
        Timeline timeline = new Timeline(new KeyFrame(Duration.seconds(1), e -> updateMetrics()));
        timeline.setCycleCount(Timeline.INDEFINITE);
        timeline.play();
    }

    private void updateBaseline() {
        try {
            lastDiskRead = Files.getFileStore(Paths.get("C:\\")).getTotalSpace(); // dummy
        } catch (Exception ignored) {}
        lastNetSent = lastNetRecv = 0;
    }

    private void updateMetrics() {
        try {
            Map<String,Object> result = AnomalyBridge.runModel();
            controller.setConnectionStatus(!result.containsKey("error"));
            if (!result.containsKey("error")) controller.updateMetrics(result);
        } catch (Exception e) {
            controller.setConnectionStatus(false);
        }

    }


    public static void main(String[] args) {
        launch();
    }
}
