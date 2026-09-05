import 'dart:io';
import 'package:flutter/material.dart';
import 'package:video_player/video_player.dart';
import 'package:image_picker/image_picker.dart';
import 'package:http/http.dart' as http;

void main() => runApp(const TikTokApp());

class TikTokApp extends StatelessWidget {
  const TikTokApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      theme: ThemeData.dark(),
      home: const MainNavigationScreen(),
    );
  }
}

class MainNavigationScreen extends StatefulWidget {
  const MainNavigationScreen({super.key});

  @override
  State<MainNavigationScreen> createState() => _MainNavigationScreenState();
}

class _MainNavigationScreenState extends State<MainNavigationScreen> {
  int _selectedIndex = 0;

  final List<Widget> _screens = [
    const HomeScreen(),
    const DiscoverScreen(),
    const UploadScreen(),
    const ChatScreen(),
    const ProfileScreen(),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: _screens[_selectedIndex],
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _selectedIndex,
        onTap: (index) => setState(() => _selectedIndex = index),
        type: BottomNavigationBarType.fixed,
        backgroundColor: Colors.black,
        selectedItemColor: Colors.white,
        unselectedItemColor: Colors.grey,
        items: const [
          BottomNavigationBarItem(icon: Icon(Icons.home), label: 'خانه'),
          BottomNavigationBarItem(icon: Icon(Icons.search), label: 'اکسپلور'),
          BottomNavigationBarItem(icon: Icon(Icons.add_box, size: 35), label: ''),
          BottomNavigationBarItem(icon: Icon(Icons.message), label: 'پیام‌ها'),
          BottomNavigationBarItem(icon: Icon(Icons.person), label: 'پروفایل'),
        ],
      ),
    );
  }
}

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  final List<String> videoUrls = const [
    'https://assets.mixkit.co/videos/preview/mixkit-tree-with-yellow-leaves-2831-large.mp4',
    'https://assets.mixkit.co/videos/preview/mixkit-mother-with-her-little-daughter-eating-vegetables-42790-large.mp4',
  ];

  @override
  Widget build(BuildContext context) {
    return PageView.builder(
      scrollDirection: Axis.vertical,
      itemCount: videoUrls.length,
      itemBuilder: (context, index) {
        return VideoTile(url: videoUrls[index], index: index + 1);
      },
    );
  }
}

class VideoTile extends StatefulWidget {
  final String url;
  final int index;
  const VideoTile({super.key, required this.url, required this.index});

  @override
  State<VideoTile> createState() => _VideoTileState();
}

class _VideoTileState extends State<VideoTile> {
  late VideoPlayerController _controller;
  bool isLiked = false;

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
    return Stack(
      children: [
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
        Positioned(
          right: 15,
          bottom: 100,
          child: Column(
            children: [
              IconButton(
                icon: Icon(Icons.favorite, color: isLiked ? Colors.red : Colors.white, size: 40),
                onPressed: () => setState(() => isLiked = !isLiked),
              ),
              const Text('12.5k'),
              const SizedBox(height: 20),
              IconButton(
                icon: const Icon(Icons.comment, color: Colors.white, size: 40),
                onPressed: () {},
              ),
              const Text('1.2k'),
            ],
          ),
        ),
      ],
    );
  }
}

class UploadScreen extends StatefulWidget {
  const UploadScreen({super.key});

  @override
  State<UploadScreen> createState() => _UploadScreenState();
}

class _UploadScreenState extends State<UploadScreen> {
  File? _videoFile;
  final ImagePicker _picker = ImagePicker();

  Future<void> _pickVideo() async {
    final XFile? video = await _picker.pickVideo(source: ImageSource.gallery);
    if (video != null) {
      setState(() {
        _videoFile = File(video.path);
      });
    }
  }

  Future<void> _uploadVideo() async {
    if (_videoFile == null) return;
    var request = http.MultipartRequest('POST', Uri.parse('http://YOUR_SERVER_IP/videos/upload'));
    request.fields['owner'] = 'my_username';
    request.fields['caption'] = 'ویدیوی جدید من';
    request.files.add(await http.MultipartFile.fromPath('file', _videoFile!.path));

    var response = await request.send();
    if (response.statusCode == 200) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('ویدیو با موفقیت آپلود شد')));
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('آپلود ویدیو جدید')),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            _videoFile != null
                ? Text('ویدیو انتخاب شد: ${_videoFile!.path.split('/').last}')
                : const Text('هنوز ویدیویی انتخاب نکرده‌اید'),
            const SizedBox(height: 20),
            ElevatedButton(onPressed: _pickVideo, child: const Text('انتخاب ویدیو از گالری')),
            const SizedBox(height: 10),
            ElevatedButton(onPressed: _uploadVideo, child: const Text('ارسال ویدیو')),
          ],
        ),
      ),
    );
  }
}

class DiscoverScreen extends StatelessWidget {
  const DiscoverScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('جستجو و کشف')),
      body: const Center(child: Text('بخش اکسپلور')),
    );
  }
}

class ChatScreen extends StatelessWidget {
  const ChatScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('پیام‌های مستقیم')),
      body: ListView.builder(
        itemCount: 5,
        itemBuilder: (context, index) => ListTile(
          leading: const CircleAvatar(child: Icon(Icons.person)),
          title: Text('کاربر ${index + 1}'),
          subtitle: const Text('سلام، ویدیو جدیدت عالی بود!'),
        ),
      ),
    );
  }
}

class ProfileScreen extends StatelessWidget {
  const ProfileScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('@my_profile')),
      body: Column(
        children: [
          const SizedBox(height: 20),
          const CircleAvatar(radius: 40, child: Icon(Icons.person, size: 40)),
          const SizedBox(height: 10),
          const Text('@my_profile', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
          const SizedBox(height: 20),
          Expanded(
            child: GridView.builder(
              gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(crossAxisCount: 3),
              itemCount: 9,
              itemBuilder: (context, index) => Container(
                margin: const EdgeInsets.all(2),
                color: Colors.grey[800],
                child: const Icon(Icons.play_arrow),
              ),
            ),
          )
        ],
      ),
    );
  }
}
