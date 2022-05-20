using System.IO.Pipes;
using System.Text;
using System.Text.Json;
using Chillax.Models;
namespace Chillax;
    public class Result
    {
        public static void Fun(string message, out ModelResponse? response)

        {
            response = new ModelResponse()
            {
                IsDepression = false,
                IsHateSpeech = false,
                IsOffensive = false,
            };
            using NamedPipeClientStream pipeClient = new(".", "ChillaxSocket", PipeDirection.InOut);
            Console.WriteLine("Attempting to connect to pipe...");
            pipeClient.Connect();
            try
            {

                using BinaryWriter _bw = new(pipeClient);
                using BinaryReader _br = new(pipeClient);
                var receivedResponse = false;
                while (!receivedResponse)
                {
                    var request = new ModelRequest() { Message = message };
                    var str = JsonSerializer.Serialize(request);

                    var buf = Encoding.ASCII.GetBytes(str);
                    _bw.Write((uint)buf.Length);
                    _bw.Write(buf);

                    Console.WriteLine($"message sent: {request.Message}");

                    var len = _br.ReadUInt32();
                    var temp = new string(_br.ReadChars((int)len));
                    Console.WriteLine("response:");
                      
                    response = JsonSerializer.Deserialize<ModelResponse>(temp);
                    Console.WriteLine($"is offensive: {response?.IsOffensive}");
                    Console.WriteLine($"is hatespeech: {response?.IsHateSpeech}");
                    Console.WriteLine($"is depression: {response?.IsDepression}");
                    Console.WriteLine($"message: {response?.Message}");
                    receivedResponse = true;
                }
            }
            // Catch the IOException that is raised if the pipe is broken
            // or disconnected.
            catch (IOException e)
            {
                Console.WriteLine("ERROR: {0}", e.Message);
            }
        }
    }

