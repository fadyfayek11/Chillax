namespace Chillax.Models;

public class ModelResponse
{
    public string Message { get; set; } = string.Empty;

    public bool IsOffensive { get; set; }

    public bool IsHateSpeech { get; set; }

    public bool IsDepression { get; set; }

    public override string ToString()
    {
        return $"Offensive:{IsOffensive}, Hatespeech:{IsHateSpeech}, Depression: {IsDepression}";
    }
}