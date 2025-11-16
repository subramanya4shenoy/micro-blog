"use client";

import { useEffect, useState } from "react";

type Post = {
  id: number;
  title: string;
  content: string;
  created_at: string;
  updated_at: string;
};

const API_URL = "http://localhost:8000";

export default function HomePage() {
  const [posts, setPosts] = useState<Post[]>([]);
  const [loading, setLoading] = useState(false);
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [error, setError] = useState<string | null>(null);

  const fetchPosts = async () => {
    try {
      setLoading(true);
      setError(null);

      const res = await fetch(`${API_URL}/posts?page=1&limit=10`);
      if (!res.ok) {
        throw new Error("Failed to fetch posts");
      }

      const data = await res.json();
      setPosts(data.posts ?? []);
    } catch (err: any) {
      setError(err.message ?? "Something went wrong");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPosts();
  }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!title.trim() || !content.trim()) {
      setError("Title and content are required");
      return;
    }

    try {
      const res = await fetch(`${API_URL}/post`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ title, content }),
      });

      if (!res.ok) {
        throw new Error("Failed to create post");
      }

      setTitle("");
      setContent("");
      await fetchPosts(); // refresh list
    } catch (err: any) {
      setError(err.message ?? "Something went wrong");
    }
  };

  const handleDelete = async (id: number) => {
    setError(null);
    try {
      const res = await fetch(`${API_URL}/post/${id}`, {
        method: "DELETE",
      });

      if (!res.ok) {
        throw new Error("Failed to delete post");
      }

      setPosts((prev) => prev.filter((p) => p.id !== id));
    } catch (err: any) {
      setError(err.message ?? "Something went wrong");
    }
  };

  return (
    <main style={{ maxWidth: 600, margin: "2rem auto", fontFamily: "system-ui" }}>
      <h1 style={{ fontSize: "1.75rem", fontWeight: 600, marginBottom: "1rem" }}>
        Microblog 📝
      </h1>

      <form onSubmit={handleCreate} style={{ marginBottom: "2rem" }}>
        <div style={{ marginBottom: "0.5rem" }}>
          <input
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Post title"
            style={{
              width: "100%",
              padding: "0.5rem",
              borderRadius: 4,
              border: "1px solid #ccc",
            }}
          />
        </div>
        <div style={{ marginBottom: "0.5rem" }}>
          <textarea
            value={content}
            onChange={(e) => setContent(e.target.value)}
            placeholder="What's on your mind?"
            rows={3}
            style={{
              width: "100%",
              padding: "0.5rem",
              borderRadius: 4,
              border: "1px solid #ccc",
              resize: "vertical",
            }}
          />
        </div>
        <button
          type="submit"
          style={{
            padding: "0.5rem 1rem",
            borderRadius: 4,
            border: "none",
            background: "#2563eb",
            color: "white",
            cursor: "pointer",
          }}
        >
          Create Post
        </button>
      </form>

      {error && (
        <p style={{ color: "red", marginBottom: "1rem" }}>
          {error}
        </p>
      )}

      {loading ? (
        <p>Loading posts...</p>
      ) : posts.length === 0 ? (
        <p>No posts yet. Create one above!</p>
      ) : (
        <ul style={{ listStyle: "none", padding: 0 }}>
          {posts.map((post) => (
            <li
              key={post.id}
              style={{
                border: "1px solid #ddd",
                borderRadius: 6,
                padding: "0.75rem",
                marginBottom: "0.75rem",
              }}
            >
              <div style={{ display: "flex", justifyContent: "space-between" }}>
                <h2 style={{ margin: 0, fontSize: "1.1rem" }}>{post.title}</h2>
                <button
                  onClick={() => handleDelete(post.id)}
                  style={{
                    border: "none",
                    background: "transparent",
                    color: "#ef4444",
                    cursor: "pointer",
                    fontSize: "0.85rem",
                  }}
                >
                  Delete
                </button>
              </div>
              <p style={{ margin: "0.5rem 0" }}>{post.content}</p>
              <p style={{ margin: 0, fontSize: "0.75rem", color: "#555" }}>
                Created: {new Date(post.created_at).toLocaleString()}
              </p>
            </li>
          ))}
        </ul>
      )}
    </main>
  );
}