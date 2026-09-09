export interface User {
  id: number;
  username: string;
  email: string;
}

export interface Store {
  id: number;
  name: string;
  slug: string;
  business_type: string;
  description: string;
  target_audience: string;
  logo: string | null;
  is_active: boolean;
  product_count: number;
  created_at: string;
}

export interface StoreProfile {
  brand_voice: string;
  tone: string;
  content_style: string;
  shipping_policy: string;
  return_policy: string;
  refund_policy: string;
  payment_info: string;
  business_rules: string;
  visual_preferences: Record<string, unknown>;
  working_hours: Record<string, unknown>;
  ai_preferences: Record<string, unknown>;
  publishing_preferences: Record<string, unknown>;
}

export interface ProductImage {
  id: number;
  image: string;
  is_main: boolean;
  alt_text: string;
  order: number;
}

export interface ProductAttribute {
  id: number;
  key: string;
  value: string;
}

export interface ProductVariant {
  id: number;
  name: string;
  attributes: Record<string, unknown>;
  price_override: string | null;
  stock_quantity: number;
  sku: string;
}

export interface Product {
  id: number;
  store: number;
  category: number | null;
  name: string;
  slug: string;
  sku: string;
  description: string;
  short_description: string;
  brand: string;
  price: string;
  compare_at_price: string | null;
  currency: string;
  stock_quantity: number;
  stock_status: string;
  tags: string[];
  is_available: boolean;
  images: ProductImage[];
  variants: ProductVariant[];
  attributes: ProductAttribute[];
  created_at: string;
}

export type JobState = "QUEUED" | "RUNNING" | "COMPLETED" | "FAILED" | "CANCELLED";

export interface Job {
  id: number;
  type: string;
  state: JobState;
  progress_step: number;
  total_steps: number;
  current_step_label: string;
  error: string;
  context: Record<string, unknown>;
  result: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

export interface Intelligence {
  id: number;
  product: number;
  summary: string;
  target_audience: string[];
  selling_points: string[];
  weaknesses: string[];
  objections: string[];
  marketing_angles: string[];
  positioning: string;
  recommended_tone: string;
  content_ideas: string[];
  use_cases: string[];
  visual_analysis: unknown[];
  updated_at: string;
}

export interface CompetitorInfo {
  name: string;
  brand: string;
  product: string;
  price: string;
  where_sells: string;
  how_sells: string;
  strengths: string[];
  weaknesses: string[];
  source: string;
}

export interface MarketConclusions {
  competitors?: CompetitorInfo[];
  comparison?: string[];
  competitor_positioning: string[];
  common_messaging: string[];
  content_patterns: string[];
  pricing_observations: string[];
  common_customer_concerns: string[];
  content_gaps: string[];
  differentiation_opportunities: string[];
  strategy_summary: string;
}

export interface WebResearchItem {
  source: string;
  title: string;
  price_toman: number | null;
  url: string;
  shops?: string;
  snippet?: string;
}

export interface MarketResearch {
  id: number;
  product: number;
  research_inputs: string;
  web_results: {
    fetched_at?: string;
    sources?: Array<{ source: string; ok: boolean; count?: number; error?: string }>;
    items?: WebResearchItem[];
  };
  observations: string[];
  conclusions: MarketConclusions;
  confidence: "LOW" | "MEDIUM" | "HIGH";
  created_at: string;
  updated_at: string;
}

export interface Caption {
  id: number;
  product: number;
  platform: string;
  tone: string;
  objective: string;
  short_text: string;
  medium_text: string;
  long_text: string;
  hashtags: string[];
  cta: string;
  about_image: number | null;
  about_video: number | null;
  about_image_url: string | null;
  about_label: string;
  created_at: string;
}

export interface GeneratedImageInfo {
  id: number;
  product: number;
  kind: "POSTER" | "PRODUCT_SHOT" | "ENHANCED";
  concept: string;
  prompt_en: string;
  style: string;
  instructions: string;
  source_image: number | null;
  image: string;
  workflow_version: string;
  /** seed/size plus, for posters, the Persian text that was drawn on by code */
  metadata: {
    seed?: number;
    width?: number;
    height?: number;
    text_overlay?: { headline: string; subline: string; badge: string };
    /** set when drawing the Persian text failed — the poster came out bare */
    text_overlay_error?: string;
  } | null;
  created_at: string;
}

export interface VideoSceneInfo {
  index: number;
  duration: number;
  visual_prompt: string;
  motion_prompt: string;
  narration: string;
  transition: "CONTINUE" | "TRANSITION" | "NEW_SCENE";
}

export interface VideoSegmentInfo {
  index: number;
  status: "PENDING" | "GENERATING" | "DONE" | "FAILED";
  anchor_source: string;
  video: string | null;
  last_frame: string | null;
  retry_count: number;
  error: string;
  updated_at: string;
}

export interface VideoScriptInfo {
  id: number;
  product: number;
  concept: string;
  objective: string;
  cta: string;
  total_duration: number;
  narration_language: "fa" | "en";
  status: "DRAFT" | "GENERATING" | "READY" | "FAILED";
  final_video: string | null;
  voice_audio: string | null;
  final_video_voiced: string | null;
  scenes: VideoSceneInfo[];
  segments: VideoSegmentInfo[];
  created_at: string;
  updated_at: string;
}

export type ApprovalState = "DRAFT" | "APPROVED" | "REJECTED" | "PUBLISHED" | "ARCHIVED";

export interface PublishJobInfo {
  id: number;
  platform: string;
  status: "PENDING" | "SENT" | "FAILED";
  attempts: number;
  last_error: string;
  published_at: string | null;
  created_at: string;
}

export interface CampaignInfo {
  id: number;
  product: number;
  name: string;
  goal: string;
  audience: string;
  notes: string;
  poster: number | null;
  product_image: number | null;
  caption: number | null;
  video_script: number | null;
  poster_detail: GeneratedImageInfo | null;
  product_image_detail: GeneratedImageInfo | null;
  caption_detail: Caption | null;
  video_script_detail: {
    id: number;
    status: string;
    total_duration: number;
    final_video: string | null;
    final_video_voiced: string | null;
  } | null;
  approval_state: ApprovalState;
  publish_jobs: PublishJobInfo[];
  created_at: string;
  updated_at: string;
}

export type ConversationState = "AI" | "HUMAN" | "ESCALATED" | "RESOLVED";

export interface ConversationInfo {
  id: number;
  state: ConversationState;
  customer: { id: number; name: string; phone: string; channel: string; created_at: string } | null;
  last_message: string;
  created_at: string;
  updated_at: string;
}

export interface ChatMessage {
  id: number;
  role: "CUSTOMER" | "AI" | "HUMAN";
  text: string;
  intent: string;
  grounding: Record<string, unknown>;
  created_at: string;
}

export interface ProductCard {
  id: number;
  name: string;
  price: string;
  currency: string;
  stock_quantity: number;
  image: string | null;
}

export interface OrderItemInfo {
  id: number;
  product: number;
  product_name: string;
  variant: number | null;
  variant_name: string | null;
  quantity: number;
  unit_price: string;
}

export type OrderStatus =
  | "DRAFT"
  | "AWAITING_RECEIPT"
  | "AWAITING_APPROVAL"
  | "CONFIRMED"
  | "CANCELLED";

export interface ReceiptInfo {
  id: number;
  image: string;
  note: string;
  status: "PENDING" | "APPROVED" | "REJECTED";
  review_note: string;
  reviewed_at: string | null;
  created_at: string;
}

export interface OrderInfo {
  id: number;
  status: OrderStatus;
  total: string;
  items: OrderItemInfo[];
  customer?: { id: number; name: string } | null;
  conversation?: number | null;
  receipts?: ReceiptInfo[];
  created_at: string;
  updated_at?: string;
}

export interface OpenOrder {
  order_id: number;
  status: OrderStatus;
  total: string;
  items: string[];
}

export interface TicketInfo {
  id: number;
  subject: string;
  description: string;
  status: "OPEN" | "IN_PROGRESS" | "RESOLVED";
  priority: "NORMAL" | "URGENT";
  customer?: { id: number; name: string } | null;
  conversation: number | null;
  resolution_note: string;
  resolved_at: string | null;
  created_at: string;
}

export interface NotificationInfo {
  id: number;
  store: number;
  store_name: string;
  type: "ESCALATION" | "ORDER" | "RECEIPT" | "TICKET" | "AI_ERROR";
  title: string;
  body: string;
  link: string;
  context: Record<string, unknown>;
  is_read: boolean;
  created_at: string;
}

export interface ChatResponse {
  conversation_id: number;
  state: ConversationState;
  message: ChatMessage | null;
  note?: string;
  action?: string;
  products?: ProductCard[];
  order?: OrderInfo | null;
  order_error?: string | null;
  payment_request?: { order_id: number; payment_info: string } | null;
  ticket?: TicketInfo | null;
  open_orders?: OpenOrder[];
}

export interface SalesDayPoint {
  date: string;
  orders: number;
  confirmed_orders: number;
  revenue: string;
}

export interface SalesData {
  days: number;
  orders: { total: number; by_status: Record<string, number> };
  revenue: { confirmed_total: string; confirmed_orders: number; avg_order_value: string };
  conversion: { conversations: number; orders: number; rate_percent: number };
  pending: { receipts: number; awaiting_approval: number; open_tickets: number };
  series: SalesDayPoint[];
  top_products: { name: string; quantity: number; revenue: string }[];
}

export interface Paginated<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}
