INSERT INTO "User" (username, nickname, email, password_hash) VALUES
('user1', 'User One', 'user1@example.com', 'password_hash_1'),
('user2', 'User Two', 'user2@example.com', 'password_hash_2'),
('user3', 'User Three', 'user3@example.com', 'password_hash_3'),
('user4', 'User Four', 'user4@example.com', 'password_hash_4'),
('user5', 'User Five', 'user5@example.com', 'password_hash_5'),
('user6', 'User Six', 'user6@example.com', 'password_hash_6'),
('user7', 'User Seven', 'user7@example.com', 'password_hash_7'),
('user8', 'User Eight', 'user8@example.com', 'password_hash_8'),
('user9', 'User Nine', 'user9@example.com', 'password_hash_9'),
('user10', 'User Ten', 'user10@example.com', 'password_hash_10'),
('user11', 'User Eleven', 'user11@example.com', 'password_hash_11'),
('user12', 'User Twelve', 'user12@example.com', 'password_hash_12'),
('user13', 'User Thirteen', 'user13@example.com', 'password_hash_13'),
('user14', 'User Fourteen', 'user14@example.com', 'password_hash_14'),
('user15', 'User Fifteen', 'user15@example.com', 'password_hash_15');


INSERT INTO Chat (chat_name) VALUES
('Chat One'),
('Chat Two'),
('Chat Three'),
('Chat Four'),
('Chat Five'),
('Chat Six'),
('Chat Seven'),
('Chat Eight'),
('Chat Nine'),
('Chat Ten'),
('Chat Eleven'),
('Chat Twelve'),
('Chat Thirteen'),
('Chat Fourteen'),
('Chat Fifteen');


INSERT INTO Connect (user_id, chat_id) VALUES
(1, 1), (2, 1), (3, 1), (4, 2), (5, 2), (6, 3),
(7, 3), (8, 4), (9, 4), (10, 5), (11, 5), (12, 6),
(13, 7), (14, 7), (15, 8), (1, 9), (2, 10), (3, 11),
(4, 12), (5, 13), (6, 14), (7, 15), (8, 1), (9, 2),
(10, 3), (11, 4), (12, 5), (13, 6), (14, 7), (15, 8),
(1, 9), (2, 10), (3, 11);


INSERT INTO Message (chat_id, sender_id, content_text) VALUES
(1, 1, 'Hello, this is the first message in Chat One'),
(1, 2, 'Hi there! How are you?'),
(1, 3, 'Im good, thanks for asking!'),
(2, 4, 'Welcome to Chat Two!'),
(2, 5, 'Looking forward to discussing here'),
(3, 6, 'Chat Three is starting!'),
(3, 7, 'Excited for this conversation'),
(4, 8, 'Hey, Chat Four is here!'),
(5, 9, 'Lets get started with Chat Five'),
(5, 10, 'Looking forward to collaborating'),
(6, 11, 'New conversation in Chat Six'),
(6, 12, 'How are you all doing?'),
(7, 13, 'Chat Seven is ready to go'),
(8, 14, 'Good to see everyone in Chat Eight'),
(9, 15, 'Chat Nine is up and running');


INSERT INTO MessageVersion (message_id, content_text, valid_from, valid_to) VALUES
(1, 'Hello, this is the first message in Chat One - v1', '2025-03-26 00:00:00', '2025-03-26 23:59:59'),
(1, 'Hello, this is the first message in Chat One - v2', '2025-03-27 00:00:00', NULL),
(2, 'Hi there! How are you? - v1', '2025-03-26 00:00:00', '2025-03-26 23:59:59'),
(2, 'Hi there! How are you? - v2', '2025-03-27 00:00:00', NULL),
(3, 'Im good, thanks for asking! - v1', '2025-03-26 00:00:00', '2025-03-26 23:59:59'),
(3, 'Im good, thanks for asking! - v2', '2025-03-27 00:00:00', NULL),
(4, 'Welcome to Chat Two! - v1', '2025-03-26 00:00:00', '2025-03-26 23:59:59'),
(5, 'Looking forward to discussing here - v1', '2025-03-26 00:00:00', '2025-03-26 23:59:59'),
(6, 'Chat Three is starting! - v1', '2025-03-26 00:00:00', '2025-03-26 23:59:59'),
(7, 'Excited for this conversation - v1', '2025-03-26 00:00:00', '2025-03-26 23:59:59'),
(8, 'Hey, Chat Four is here! - v1', '2025-03-26 00:00:00', '2025-03-26 23:59:59'),
(9, 'Lets get started with Chat Five - v1', '2025-03-26 00:00:00', '2025-03-26 23:59:59'),
(10, 'Looking forward to collaborating - v1', '2025-03-26 00:00:00', '2025-03-26 23:59:59'),
(11, 'New conversation in Chat Six - v1', '2025-03-26 00:00:00', '2025-03-26 23:59:59');


INSERT INTO Channel (channel_name, description, owner_id) VALUES
('Channel One', 'This is the first channel', 1),
('Channel Two', 'Channel for discussions', 2),
('Channel Three', 'Tech related discussions', 3),
('Channel Four', 'General discussions', 4),
('Channel Five', 'Music lovers channel', 5),
('Channel Six', 'Gaming community', 6),
('Channel Seven', 'Movie discussions', 7),
('Channel Eight', 'Food lovers', 8),
('Channel Nine', 'Travel enthusiasts', 9),
('Channel Ten', 'Health and fitness', 10),
('Channel Eleven', 'Education and study tips', 11),
('Channel Twelve', 'Photography lovers', 12),
('Channel Thirteen', 'Programming discussions', 13),
('Channel Fourteen', 'Sports updates', 14),
('Channel Fifteen', 'Art and culture', 15);


INSERT INTO Post (channel_id, author_id, content_text) VALUES
(1, 1, 'Welcome to Channel One!'),
(2, 2, 'This is a channel for all tech enthusiasts'),
(3, 3, 'Lets talk about programming!'),
(4, 4, 'General discussions happen here'),
(5, 5, 'For all music lovers!'),
(6, 6, 'Gaming time!'),
(7, 7, 'Movies to watch this weekend'),
(8, 8, 'Lets share our favorite foods'),
(9, 9, 'Who has traveled to Europe?'),
(10, 10, 'Fitness tips for beginners'),
(11, 11, 'How to improve study habits'),
(12, 12, 'Photography tips and tricks'),
(13, 13, 'Best coding practices'),
(14, 14, 'Latest sports news'),
(15, 15, 'Art exhibitions around the world');


INSERT INTO Subscription (user_id, channel_id) VALUES
(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6),
(7, 7), (8, 8), (9, 9), (10, 10), (11, 11), (12, 12),
(13, 13), (14, 14), (15, 15), (1, 2), (2, 3), (3, 4),
(4, 5), (5, 6), (6, 7), (7, 8), (8, 9), (9, 10),
(10, 11), (11, 12), (12, 13), (13, 14), (14, 15), (15, 1);
