
import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.nio.charset.StandardCharsets;

public class BillingBridge {
    public static void main(String[] args) throws Exception {
        String projectDir = System.getProperty("user.dir");

        String python = projectDir
                + "\\.venv\\Scripts\\python.exe";

        ProcessBuilder builder = new ProcessBuilder(
                python,
                "-m",
                "app.integrations.adapter_worker"
        );

        builder.directory(new java.io.File(projectDir));
        builder.redirectError(ProcessBuilder.Redirect.INHERIT);

        Process process = builder.start();

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
            String request =
                "{\"arguments\":{\"unit_price\":\"12.50\",\"quantity\":4}}";

            writer.write(request);
            writer.newLine();
            writer.flush();
            writer.close();

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
