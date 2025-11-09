package com.dheeraj.systemanomalymonitor;

import javafx.application.Application;
import javafx.fxml.FXMLLoader;
import javafx.scene.Parent;
import javafx.scene.Scene;
import javafx.stage.Stage;

public class MainApp extends Application {

    @Override
    public void start(Stage primaryStage) {
        try {
            // Load the dashboard.fxml file from resources
            FXMLLoader loader = new FXMLLoader(
                    getClass().getResource("/com/dheeraj/systemanomalymonitor/dashboard.fxml")
            );
            Parent root = loader.load();

            // (Optional) Get the controller if you want to call methods on it
            DashboardController controller = loader.getController();

            // Set up and show the window
            Scene scene = new Scene(root);
            primaryStage.setTitle("🧠 System Anomaly Monitor");
            primaryStage.setScene(scene);
            primaryStage.show();

        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    public static void main(String[] args) {
        launch(args);
    }
}
