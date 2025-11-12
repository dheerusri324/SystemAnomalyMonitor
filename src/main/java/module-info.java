module com.dheeraj.systemanomalymonitor {
    requires javafx.controls;
    requires javafx.fxml;
    requires jdk.management;
    requires org.slf4j;

    requires org.controlsfx.controls; // if you added ControlsFX
    requires org.kordamp.bootstrapfx.core;
    requires com.fasterxml.jackson.databind; // if you added BootstrapFX

    opens com.dheeraj.systemanomalymonitor to javafx.fxml;
    exports com.dheeraj.systemanomalymonitor;
}
