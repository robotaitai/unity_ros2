using UnityEngine;
using ROS2;
using System.Collections.Concurrent;

public class ROS2ListenerImage : MonoBehaviour
{
    private ROS2UnityComponent ros2Unity;
    private ROS2Node ros2Node;
    private ISubscription<sensor_msgs.msg.Image> imageSubscriber;
    public Material ImageListenerMaterial;
    private ConcurrentQueue<byte[]> imageQueue = new ConcurrentQueue<byte[]>();

    void Start()
    {
        ros2Unity = GetComponent<ROS2UnityComponent>();
    }

    void Update()
    {
        if (ros2Node == null && ros2Unity.Ok())
        {
            ros2Node = ros2Unity.CreateNode("ROS2UnityImageSubscriber");
            imageSubscriber = ros2Node.CreateSubscription<sensor_msgs.msg.Image>(
                "/taio/image", HandleImageMessage);
        }

        if (imageQueue.TryDequeue(out byte[] imageData))
        {
            Texture2D texture = ConvertImageMessageToTexture(imageData, 640, 480); // Example width and height
            if (ImageListenerMaterial != null)
            {
                ImageListenerMaterial.mainTexture = texture;
            }
        }
    }

    private Texture2D ConvertImageMessageToTexture(byte[] imageData, int width, int height)
    {
        Texture2D texture = new Texture2D(width, height, TextureFormat.RGB24, false);
        texture.LoadRawTextureData(imageData);
        texture.Apply();
        return texture;
    }

    private void HandleImageMessage(sensor_msgs.msg.Image msg)
    {
        imageQueue.Enqueue(msg.Data);
    }

    void OnDestroy()
    {
        if (ros2Node != null)
        {
            // Cleanup if needed
        }
    }
}
