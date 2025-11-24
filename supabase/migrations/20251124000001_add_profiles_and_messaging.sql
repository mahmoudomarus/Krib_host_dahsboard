-- Add avatar and profile fields to users table
ALTER TABLE public.users 
ADD COLUMN IF NOT EXISTS avatar_url TEXT,
ADD COLUMN IF NOT EXISTS bio TEXT,
ADD COLUMN IF NOT EXISTS phone_number TEXT,
ADD COLUMN IF NOT EXISTS notification_email BOOLEAN DEFAULT TRUE,
ADD COLUMN IF NOT EXISTS notification_sms BOOLEAN DEFAULT FALSE;

-- Create messages table for guest-host communication
CREATE TABLE IF NOT EXISTS public.messages (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  conversation_id UUID NOT NULL,
  sender_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
  sender_type TEXT NOT NULL CHECK (sender_type IN ('host', 'guest', 'ai')),
  content TEXT NOT NULL,
  is_ai_generated BOOLEAN DEFAULT FALSE,
  metadata JSONB DEFAULT '{}',
  is_read BOOLEAN DEFAULT FALSE,
  read_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create conversations table
CREATE TABLE IF NOT EXISTS public.conversations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  property_id UUID REFERENCES public.properties(id) ON DELETE CASCADE,
  booking_id UUID REFERENCES public.bookings(id) ON DELETE SET NULL,
  host_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
  guest_id UUID,
  guest_name TEXT,
  guest_email TEXT,
  status TEXT DEFAULT 'active' CHECK (status IN ('active', 'archived', 'closed')),
  last_message_at TIMESTAMPTZ DEFAULT NOW(),
  unread_count_host INTEGER DEFAULT 0,
  unread_count_guest INTEGER DEFAULT 0,
  metadata JSONB DEFAULT '{}',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_messages_conversation_id ON public.messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_messages_sender_id ON public.messages(sender_id);
CREATE INDEX IF NOT EXISTS idx_messages_created_at ON public.messages(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_conversations_host_id ON public.conversations(host_id);
CREATE INDEX IF NOT EXISTS idx_conversations_property_id ON public.conversations(property_id);
CREATE INDEX IF NOT EXISTS idx_conversations_booking_id ON public.conversations(booking_id);
CREATE INDEX IF NOT EXISTS idx_conversations_last_message_at ON public.conversations(last_message_at DESC);

-- RLS policies for messages
ALTER TABLE public.messages ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view messages in their conversations"
  ON public.messages FOR SELECT
  USING (
    EXISTS (
      SELECT 1 FROM public.conversations c
      WHERE c.id = messages.conversation_id
      AND (c.host_id = (SELECT auth.uid()) OR sender_id = (SELECT auth.uid()))
    )
  );

CREATE POLICY "Users can create messages in their conversations"
  ON public.messages FOR INSERT
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM public.conversations c
      WHERE c.id = conversation_id
      AND (c.host_id = (SELECT auth.uid()) OR sender_id = (SELECT auth.uid()))
    )
  );

-- RLS policies for conversations
ALTER TABLE public.conversations ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Hosts can view their conversations"
  ON public.conversations FOR SELECT
  USING (host_id = (SELECT auth.uid()));

CREATE POLICY "Hosts can create conversations"
  ON public.conversations FOR INSERT
  WITH CHECK (host_id = (SELECT auth.uid()));

CREATE POLICY "Hosts can update their conversations"
  ON public.conversations FOR UPDATE
  USING (host_id = (SELECT auth.uid()));

-- Function to update conversation timestamp on new message
CREATE OR REPLACE FUNCTION public.update_conversation_timestamp()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
  UPDATE public.conversations
  SET 
    last_message_at = NOW(),
    unread_count_host = CASE 
      WHEN NEW.sender_type = 'guest' THEN unread_count_host + 1
      ELSE unread_count_host
    END,
    unread_count_guest = CASE 
      WHEN NEW.sender_type = 'host' THEN unread_count_guest + 1
      ELSE unread_count_guest
    END,
    updated_at = NOW()
  WHERE id = NEW.conversation_id;
  
  RETURN NEW;
END;
$$;

-- Trigger to update conversation on new message
DROP TRIGGER IF EXISTS trigger_update_conversation_timestamp ON public.messages;
CREATE TRIGGER trigger_update_conversation_timestamp
AFTER INSERT ON public.messages
FOR EACH ROW
EXECUTE FUNCTION public.update_conversation_timestamp();

-- Function to mark messages as read
CREATE OR REPLACE FUNCTION public.mark_messages_read(
  p_conversation_id UUID,
  p_user_type TEXT
)
RETURNS void
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
  UPDATE public.messages
  SET is_read = TRUE, read_at = NOW()
  WHERE conversation_id = p_conversation_id
  AND is_read = FALSE
  AND sender_type != p_user_type;
  
  UPDATE public.conversations
  SET 
    unread_count_host = CASE WHEN p_user_type = 'host' THEN 0 ELSE unread_count_host END,
    unread_count_guest = CASE WHEN p_user_type = 'guest' THEN 0 ELSE unread_count_guest END
  WHERE id = p_conversation_id;
END;
$$;

