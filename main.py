import 'package:flutter/material.dart';
import 'package:video_player/video_player.dart';

void main() => runApp(const TikTokApp());

class TikTokApp extends StatelessWidget {
  const TikTokApp({super.key});

  @override
  Widget build(BuildContext context) {
    return const MaterialApp(
      debugShowCheckedModeBanner: false,
      home: VideoFeedScreen(),
    );
  }
}

class VideoFeedScreen extends StatefulWidget {
  const VideoFeedScreen({super.key});

  @override
  State<VideoFeedScreen> createState() => _VideoFeedScreenState();
}

class _VideoFeedScreenState extends State<VideoFeedScreen> {
  final List<Map<String, dynamic>> _videos = [
    {
      'url': 'https://assets.mixkit.co/videos/preview/mixkit-tree-with-yellow-leaves-2831-large.mp4',
      'username': '@user1',
      'caption': 'اولین ویدیو من! #تیک_تاک',
      'likes': 120,
    },
    {
      'url': 'https://assets.mixkit.co/videos/preview/mixkit-mother-with-her-little-daughter-eating-vegetables-42790-large.mp4',
      'username': '@user2',
      'caption': 'روز خوب همگی بخیر ✨',
      'likes': 450,
    },
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.black,
      body: PageView.builder(
        scrollDirection: Axis.vertical,
        itemCount: _videos.length,
        itemBuilder: (context, index) {
          return TikTokVideoTile(videoData: _videos[index]);
        },
      ),
    );
  }
}

class TikTokVideoTile extends StatefulWidget {
  final Map<String, dynamic> videoData;
  const TikTokVideoTile({super.key, required this.videoData});

  @override
  State<TikTokVideoTile> createState() => _TikTokVideoTileState();
}

class _TikTokVideoTileState extends State<TikTokVideoTile> {
  late VideoPlayerController _controller;
  bool isLiked = false;

  @override
  void initState() {
    super.initState();
    _controller = VideoPlayerController.networkUrl(Uri.parse(widget.videoData['url']))
      ..initialize().then((_) {
        setState(() {});
        _controller.play();
        _controller.setLooping(true);
      });
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Stack(
      children: [
        // پخش‌کننده ویدیو
        _controller.value.isInitialized
            ? SizedBox.expand(
                child: FittedBox(
                  fit: BoxFit.cover,
                  child: SizedBox(
                    width: _controller.value.size.width,
                    height: _controller.value.size.height,
                    child: VideoPlayer(_controller),
                  ),
                ),
              )
            : const Center(child: CircularProgressIndicator()),

        // دکمه‌های سمت راست (لایک و کامنت)
        Positioned(
          right: 15,
          bottom: 100,
          child: Column(
            children: [
              IconButton(
                icon: Icon(
                  Icons.favorite,
                  color: isLiked ? Colors.red : Colors.white,
                  size: 40,
                ),
                onPressed: () {
                  setState(() {
                    isLiked = !isLiked;
                  });
                },
              ),
              Text(
                '${widget.videoData['likes'] + (isLiked ? 1 : 0)}',
                style: const TextStyle(color: Colors.white),
              ),
              const SizedBox(height: 20),
              IconButton(
                icon: const Icon(Icons.comment, color: Colors.white, size: 40),
                onPressed: () {
                  // نمایش بخش کامنت‌ها
                },
              ),
              const Text('کامنت', style: TextStyle(color: Colors.white)),
            ],
          ),
        ),

        // اطلاعات کپشن و آیدی
        Positioned(
          left: 15,
          bottom: 30,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                widget.videoData['username'],
                style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 16),
              ),
              const SizedBox(height: 5),
              Text(
                widget.videoData['caption'],
                style: const TextStyle(color: Colors.white),
              ),
            ],
          ),
        )
      ],
    );
  }
}
