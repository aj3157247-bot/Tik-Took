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
  // لینک‌های نمونه برای تست
  final List<String> _videoUrls = [
    'https://assets.mixkit.co/videos/preview/mixkit-tree-with-yellow-leaves-2831-large.mp4',
    'https://assets.mixkit.co/videos/preview/mixkit-mother-with-her-little-daughter-eating-vegetables-42790-large.mp4',
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: PageView.builder(
        scrollDirection: Axis.vertical, // اسکرول عمودی شبیه تیک‌تاک
        itemCount: _videoUrls.length,
        itemBuilder: (context, index) {
          return TikTokVideoItem(url: _videoUrls[index]);
        },
      ),
    );
  }
}

class TikTokVideoItem extends StatefulWidget {
  final String url;
  const TikTokVideoItem({super.key, required this.url});

  @override
  State<TikTokVideoItem> createState() => _TikTokVideoItemState();
}

class _TikTokVideoItemState extends State<TikTokVideoItem> {
  late VideoPlayerController _controller;

  @override
  void initState() {
    super.initState();
    _controller = VideoPlayerController.networkUrl(Uri.parse(widget.url))
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
    return _controller.value.isInitialized
        ? AspectRatio(
            aspectRatio: _controller.value.aspectRatio,
            child: VideoPlayer(_controller),
          )
        : const Center(child: CircularProgressIndicator());
  }
}
