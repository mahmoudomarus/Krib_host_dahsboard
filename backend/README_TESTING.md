# Testing Messaging & Notifications

## Prerequisites

1. Backend running
2. Environment variables set (especially OPENAI_API_KEY, RESEND_API_KEY)
3. SQL migration for messaging run: `supabase/migrations/20251124000001_add_profiles_and_messaging.sql`

## Test Messaging System

```bash
cd backend
source venv/bin/activate
python test_messaging.py
```

What it does:
- Creates a test conversation with a guest
- Adds test messages
- Generates AI response
- Sends email notification
- Lists all conversations and messages

Expected output:
- New conversation appears in Messages tab
- Email notification received
- AI can generate responses
- Messages properly threaded

## Test Notifications

```bash
cd backend
source venv/bin/activate
python test_notifications.py
```

What it does:
- Creates 5 different notification types:
  - New Booking
  - Payment Received
  - New Message
  - Review Received
  - Payout Processed
- Sends test emails for each type
- Lists all notifications

Expected output:
- Notifications appear in notification bell
- Email notifications received (if opted in)
- Notifications can be marked as read
- Click notifications navigate to correct pages

## Manual Testing in UI

### Messaging System
1. Run `python test_messaging.py`
2. Go to https://host.krib.ae/dashboard/messages
3. You should see test conversation
4. Click to open conversation
5. View messages
6. Try replying
7. Test AI response generation button
8. Test archiving conversation

### Notifications
1. Run `python test_notifications.py`
2. Go to https://host.krib.ae/dashboard
3. Click notification bell icon (top right)
4. See all test notifications
5. Click on each notification
6. Verify navigation works
7. Mark as read/unread
8. Check email inbox for notification emails

## Cleanup Test Data

After testing, you can clean up:

```sql
-- Delete test conversations
DELETE FROM public.conversations WHERE guest_email = 'test.guest@example.com';

-- Delete test notifications
DELETE FROM public.notifications WHERE title LIKE '%Test%' OR type IN ('new_booking', 'payment_received');
```

## Troubleshooting

### Messaging Test Fails
- Check `OPENAI_API_KEY` is set
- Check database migration is run
- Check RLS policies allow insert

### Email Not Received
- Check `RESEND_API_KEY` is set
- Check `FROM_EMAIL` is verified in Resend dashboard
- Check spam folder
- Check Resend logs for delivery status

### Notifications Not Showing
- Check database has notifications table
- Check RLS policies
- Hard refresh browser (Cmd+Shift+R)
- Check browser console for errors
