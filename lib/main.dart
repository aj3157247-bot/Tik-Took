import 'package:flutter/material.dart';

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
    const Center(child: Text('جستجو و کشف (Discover)')),
    const Center(child: Text('آپلود ویدیو (+)')),
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

// --- ۱. صفحه اصلی (Feed) ---
class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return PageView.builder(
      scrollDirection: Axis.vertical,
      itemCount: 5,
      itemBuilder: (context, index) {
        return Container(
          color: Colors.black,
          child: Stack(
            children: [
              Center(
                child: Text('ویدیو شماره ${index + 1}', style: const TextStyle(fontSize: 24)),
              ),
              Positioned(
                right: 15,
                bottom: 100,
                child: Column(
                  children: [
                    IconButton(icon: const Icon(Icons.favorite, color: Colors.red, size: 40), onPressed: () {}),
                    const Text('12.5k'),
                    const SizedBox(height: 20),
                    IconButton(icon: const Icon(Icons.comment, color: Colors.white, size: 40), onPressed: () {}),
                    const Text('1.2k'),
                    const SizedBox(height: 20),
                    IconButton(icon: const Icon(Icons.share, color: Colors.white, size: 40), onPressed: () {}),
                    const Text('اشتراک'),
                  ],
                ),
              )
            ],
          ),
        );
      },
    );
  }
}

// --- ۲. صفحه چت (Direct Messages) ---
class ChatScreen extends StatelessWidget {
  const ChatScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('پیام‌های مستقیم'), backgroundColor: Colors.black),
      body: ListView.builder(
        itemCount: 10,
        itemBuilder: (context, index) {
          return ListTile(
            leading: const CircleAvatar(backgroundColor: Colors.blue, child: Icon(Icons.person)),
            title: Text('کاربر ${index + 1}'),
            subtitle: const Text('آخرین پیام ارسال شده...'),
            trailing: const Icon(Icons.arrow_forward_ios, size: 15),
          );
        },
      ),
    );
  }
}

// --- ۳. صفحه پروفایل (Profile) ---
class ProfileScreen extends StatelessWidget {
  const ProfileScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('@my_username'), backgroundColor: Colors.black),
      body: Column(
        children: [
          const SizedBox(height: 20),
          const CircleAvatar(radius: 50, child: Icon(Icons.person, size: 50)),
          const SizedBox(height: 10),
          const Text('@my_username', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
          const SizedBox(height: 15),
          const Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Column(children: [Text('120', style: TextStyle(fontWeight: FontWeight.bold)), Text('دنبال‌شونده')]),
              SizedBox(width: 30),
              Column(children: [Text('4.5K', style: TextStyle(fontWeight: FontWeight.bold)), Text('دنبال‌کننده')]),
              SizedBox(width: 30),
              Column(children: [Text('90K', style: TextStyle(fontWeight: FontWeight.bold)), Text('لایک‌ها')]),
            ],
          ),
          const Divider(height: 30),
          Expanded(
            child: GridView.builder(
              gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(crossAxisCount: 3, crossAxisSpacing: 2, mainAxisSpacing: 2),
              itemCount: 12,
              itemBuilder: (context, index) => Container(color: Colors.grey[900], child: const Icon(Icons.play_arrow)),
            ),
          )
        ],
      ),
    );
  }
}
