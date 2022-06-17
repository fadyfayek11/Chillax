using System.IO.Pipes;
using System.Security.AccessControl;
using System.Text;
using System.Text.Json;
using Chillax.Models;
namespace Chillax;
    public class Result
    {
        public static async Task<ModelResponse> GetPredictions(string message)
        {
            await using NamedPipeClientStream pipeClient = new(".", "ChillaxSocket", PipeDirection.InOut);
            Console.WriteLine("Attempting to connect to model server pipe...");
            await pipeClient.ConnectAsync();
            Console.WriteLine("Connection successful");
            try
            {
                while (true)
                {
                    var request = new ModelRequest() {Message = message};
                    var str = JsonSerializer.Serialize(request);
                    var buf = Encoding.UTF8.GetBytes(str);
                    await pipeClient.WriteAsync(Encoding.UTF8.GetBytes(buf.Length.ToString()));
                    await pipeClient.WriteAsync(buf);

                    Console.WriteLine($"message sent: {request.Message}");

                    var lenBuffer = new byte[4];
                    var _ = await pipeClient.ReadAsync(lenBuffer.AsMemory(0, lenBuffer.Length));
                    var messageBuffer = new byte[BitConverter.ToInt32(lenBuffer)];
                    _ = await pipeClient.ReadAsync(messageBuffer.AsMemory(0, messageBuffer.Length));
                    var temp = Encoding.UTF8.GetString(messageBuffer);
                    var modelServerResponse = JsonSerializer.Deserialize<ModelResponse>(temp, new JsonSerializerOptions(JsonSerializerDefaults.Web));
                    return modelServerResponse ?? new ModelResponse();
                }
            }
            catch (IOException e)
            {
                Console.WriteLine("ERROR: {0}", e.Message);
            }
            return new ModelResponse();
        }
    }

