import logging
import os
import datetime
from concurrent import futures

import grpc
import google.protobuf.json_format as json_format

from lib import crud
from lib.database import get_db

from lib.proto import social_engine_pb2 as pb
from lib.proto import social_engine_pb2_grpc as pb_service


SERVICE_PORT = int(os.environ.get("SERVICE_PORT"))
SERVICE_MAX_WORKERS_COUNT = int(os.environ.get("SERVICE_MAX_WORKERS_COUNT"))
PAGE_SIZE = int(os.environ.get("PAGE_SIZE"))


class SocialEngine(pb_service.SocialEngineServicer):
    def CreatePost(self, post_request: pb.PostRequest, context):
        logging.info('CreatePost new post request: {}'.format(json_format.MessageToDict(post_request)))

        if post_request.request_user_id != post_request.post.user_id:
            return pb.PostResponse(
                post=post_request.post,
                code=403,
                description="access denied"
            )

        try:
            posts_repository = crud.PostsRepository(db_session)
            created_db_post = posts_repository.create_one(post_request.post)

            created_db_post.fill_proto(post_request.post)
        except:
            return pb.PostResponse(
                post=post_request.post,
                code=400,
                description="incorrect input"
            )

        return pb.PostResponse(
            post=post_request.post,
            code=200,
        )
    
    def UpdatePost(self, post_request: pb.PostRequest, context):
        logging.info('UpdatePost new post request: {}'.format(json_format.MessageToDict(post_request)))

        if post_request.request_user_id != post_request.post.user_id:
            return pb.PostResponse(
                post=post_request.post,
                code=403,
                description="access denied"
            )

        try:
            posts_repository = crud.PostsRepository(db_session)

            if not posts_repository.check_exists(post_request.post.id):
                return pb.PostResponse(
                    post=post_request.post,
                    code=404,
                    description="post not found"
                )

            post = posts_repository.get_one(post_request.post.id)
            
            if post_request.post.user_id != post.user_id:
                return pb.PostResponse(
                    post=post_request.post,
                    code=400,
                    description="unable to change author"
                )
            
            post.title = post_request.post.title
            post.text = post_request.post.text
            posts_repository.commit()

            post.fill_proto(post_request.post)
        except:
            return pb.PostResponse(
                post=post_request.post,
                code=400,
                description="incorrect input"
            )

        return pb.PostResponse(
            post=post_request.post,
            code=200,
        )
    
    def DeletePost(self, post_request: pb.PostRequest, context):
        logging.info('DeletePost new post request: {}'.format(json_format.MessageToDict(post_request)))

        if post_request.post.user_id and post_request.request_user_id != post_request.post.user_id:
            return pb.PostResponse(
                post=post_request.post,
                code=403,
                description="access denied"
            )

        try:
            posts_repository = crud.PostsRepository(db_session)

            if not posts_repository.check_exists(post_request.post.id):
                return pb.PostResponse(
                    post=post_request.post,
                    code=404,
                    description="post not found"
                )
            
            post = posts_repository.get_one(post_request.post.id)

            if post_request.request_user_id != post.user_id:
                return pb.PostResponse(
                    post=post_request.post,
                    code=403,
                    description="access denied"
                )

            posts_repository.delete_one(post_request.post.id)
        except:
            return pb.PostResponse(
                post=post_request.post,
                code=400,
                description="incorrect input"
            )

        return pb.PostResponse(
            post=post_request.post,
            code=200,
        )
    
    def GetPost(self, post_request: pb.PostRequest, context):
        logging.info('GetPost new post request: {}'.format(json_format.MessageToDict(post_request)))

        if post_request.post.user_id and post_request.request_user_id != post_request.post.user_id:
            return pb.PostResponse(
                post=post_request.post,
                code=403,
                description="access denied"
            )

        try:
            posts_repository = crud.PostsRepository(db_session)

            if not posts_repository.check_exists(post_request.post.id):
                return pb.PostResponse(
                    post=post_request.post,
                    code=404,
                    description="post not found"
                )

            post = posts_repository.get_one(post_request.post.id)
            
            if post_request.request_user_id != post.user_id:
                return pb.PostResponse(
                    post=post_request.post,
                    code=403,
                    description="access denied"
                )
            
            post.fill_proto(post_request.post)
        except:
            return pb.PostResponse(
                post=post_request.post,
                code=400,
                description="incorrect input"
            )

        return pb.PostResponse(
            post=post_request.post,
            code=200,
        )
    
    def GetUserPosts(self, post_request: pb.PostRequest, context):
        logging.info('GetUserPosts new post request: {}'.format(json_format.MessageToDict(post_request)))

        if post_request.request_user_id != post_request.post.user_id:
            yield pb.PostResponse(
                post=post_request.post,
                code=403,
                description="access denied"
            )
        else:
            try:
                posts_repository = crud.PostsRepository(db_session)

                posts = posts_repository.get_with_pagination(
                    post_request.post.user_id,
                    post_request.post.id,
                    PAGE_SIZE
                )

                for post in posts:
                    post.fill_proto(post_request.post)

                    yield pb.PostResponse(
                        post=post_request.post,
                        code=200,
                    )
            except:
                yield pb.PostResponse(
                    post=post_request.post,
                    code=400,
                    description="incorrect input"
                )


def serve():
    for opened_db_session in get_db():
        global db_session
        db_session = opened_db_session

        server = grpc.server(futures.ThreadPoolExecutor(max_workers=SERVICE_MAX_WORKERS_COUNT))
        pb_service.add_SocialEngineServicer_to_server(SocialEngine(), server)
        port = SERVICE_PORT
        server.add_insecure_port(f"[::]:{port}")
        server.start()
        logging.info(f"SocialEngine Server started on port {port}")

        server.wait_for_termination()


if __name__ == "__main__":
    serve()
