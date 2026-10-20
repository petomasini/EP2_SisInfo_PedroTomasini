-- RADAR TECH: 5 consultas solicitadas no enunciado.
-- IDs usados: post 1 possui comentarios; categoria 3 = Desenvolvimento Web.

-- 1. Todos os posts, do mais recente para o mais antigo.
SELECT *
FROM blog_post
ORDER BY published_at DESC;

-- 2. Todos os comentarios de um post, mais recentes primeiro.
SELECT *
FROM blog_comment
WHERE post_id = 1
ORDER BY published_at DESC;

-- 3. Colunas do comentario exceto post_id, acrescidas de titulo e post_date.
SELECT c.id, c.author_id, c.text, c.published_at,
       p.title, p.published_at AS post_date
FROM blog_comment AS c
INNER JOIN blog_post AS p ON p.id = c.post_id
WHERE c.post_id = 1
ORDER BY c.published_at DESC;

-- 4. Todas as colunas da categoria e dos posts que pertencem a ela.
SELECT cat.*, p.*
FROM blog_category AS cat
INNER JOIN blog_post_categories AS pc ON pc.category_id = cat.id
INNER JOIN blog_post AS p ON p.id = pc.post_id
WHERE cat.id = 3
ORDER BY p.published_at DESC;

-- 5. Categorias associadas a dois ou mais posts.
SELECT cat.id, cat.name, cat.description,
       COUNT(DISTINCT pc.post_id) AS total_posts
FROM blog_category AS cat
INNER JOIN blog_post_categories AS pc ON pc.category_id = cat.id
GROUP BY cat.id, cat.name, cat.description
HAVING COUNT(DISTINCT pc.post_id) >= 2
ORDER BY total_posts DESC, cat.name;
