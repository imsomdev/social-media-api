from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework.parsers import MultiPartParser, FormParser
from api.models import Post, Like, Comment
from .serializers import PostSerializer, PostCommentSerializer


class CreatePostView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]  # Accept form-data

    def post(self, request):
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)  # Assign the current user to the post
            return Response({"message": "new post created successfully"}, 201)
        return Response(serializer.errors, 400)

    def get(self, request):
        posts = Post.objects.all().order_by("-created_at")
        serializer = PostSerializer(
            posts,
            many=True,
            context={"request": request},
        )
        return Response(serializer.data, 200)


class DeletePostView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        post_id = request.data.get("post_id")
        if post_id:
            try:
                post = Post.objects.get(id=post_id)
                if post.user == request.user:
                    post.delete()
                    return Response({"message": "Post deleted successfully"}, 200)
                else:
                    return Response(
                        {"message": "You are not authorized to delete this post."}, 403
                    )
            except Post.DoesNotExist:
                return Response({"message": "Post not found."}, 404)
        else:
            return Response({"message": "Missing post_id in request data."}, 400)


class ToggleLikeAPIView(APIView):
    def post(self, request):
        post_id = request.data.get("post_id")
        post = Post.objects.get(id=post_id)
        user = request.user

        like = Like.objects.filter(user=user, post=post).first()
        if like:
            like.delete()
            post.increment_likes_count(-1)
            return Response({"message": "Like removed."}, 200)
        else:
            Like.objects.create(user=user, post=post)
            post.increment_likes_count(1)
            return Response({"message": "Post liked."}, 201)


class PostCommentView(APIView):
    def post(self, request):
        serializer = PostCommentSerializer(
            data=request.data,
            context={"request": request},
        )
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Comment created successfully"}, status=201)
        return Response(serializer.errors, 400)

    def get(self, request):
        comment = Comment.objects.all().order_by("-created_at")
        serializer = PostCommentSerializer(
            comment,
            many=True,
            context={"request": request},
        )
        return Response(serializer.data, 200)
