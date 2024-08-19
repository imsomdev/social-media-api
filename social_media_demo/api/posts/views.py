from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework.parsers import MultiPartParser, FormParser
from api.models import PostModel
from .serializers import PostSerializer


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
        posts = PostModel.objects.all().order_by("-created_at")
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data, 200)


class DeletePostView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        post_id = request.data.get("post_id")
        if post_id:
            try:
                post = PostModel.objects.get(id=post_id)
                if post.user == request.user:
                    post.delete()
                    return Response({"message": "Post deleted successfully"}, 200)
                else:
                    return Response(
                        {"message": "You are not authorized to delete this post."}, 403
                    )
            except PostModel.DoesNotExist:
                return Response({"message": "Post not found."}, 404)
        else:
            return Response({"message": "Missing post_id in request data."}, 400)
