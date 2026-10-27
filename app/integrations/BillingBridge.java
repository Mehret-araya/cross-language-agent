
import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.nio.charset.StandardCharsets;

public class BillingBridge {
    public static void main(String[] args) throws Exception {
        // Use the Python interpreter selected by the caller when available.
        String projectDir = System.getProperty("user.dir");
        String python = args.length > 0 ? args[0] : "python";

        // Start the Python worker.
        ProcessBuilder builder = new ProcessBuilder(
                python,
                "-m",
                "app.integrations.adapter_worker"
        );

        builder.directory(new File(projectDir));
        builder.redirectError(ProcessBuilder.Redirect.INHERIT);

        Process process = builder.start();

        // Read the JSON request supplied to this Java program.
        String request = new String(
                System.in.readAllBytes(),
                StandardCharsets.UTF_8
        ).trim();

        // Use a default request if no input was provided.
        if (request.isEmpty()) {
            request = "{\"arguments\":{\"unit_price\":\"12.50\",\"quantity\":4}}";
        }

        try (
                BufferedWriter writer = new BufferedWriter(
                        new OutputStreamWriter(
                                process.getOutputStream(),
                                StandardCharsets.UTF_8
                        )
                );
                BufferedReader reader = new BufferedReader(
                        new InputStreamReader(
                                process.getInputStream(),
                                StandardCharsets.UTF_8
                        )
                )
        ) {
            // Send the JSON request to Python.
            writer.write(request);
            writer.newLine();
            writer.flush();
            writer.close();

            // Read Python's JSON response.
            String response = reader.readLine();
            int exitCode = process.waitFor();

            if (exitCode != 0) {
                throw new RuntimeException(
                        "Python worker exited with code " + exitCode
                );
            }

            if (response == null) {
                throw new RuntimeException(
                        "Python worker returned no response."
                );
            }

            System.out.println("Response from Python:");
            System.out.println(response);
        }
    }
}
