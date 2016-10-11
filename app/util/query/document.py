from app.models.document import DocumentModel
from app.models.user import UserModel


def getDocumentQuery(document_id):
    return DocumentModel.query. \
        with_entities(DocumentModel.id,
                      DocumentModel.title,
                      DocumentModel.content,
                      DocumentModel.read_count,
                      DocumentModel.like_count,
                      DocumentModel.user_id,
                      UserModel.username.label('username'),
                      DocumentModel.created_date). \
        filter(DocumentModel.user_id == UserModel.id). \
        filter_by(id=document_id)


def getDocumentListQuery():
    return DocumentModel.query. \
        with_entities(DocumentModel.id,
                      DocumentModel.title,
                      DocumentModel.content,
                      DocumentModel.read_count,
                      DocumentModel.like_count,
                      DocumentModel.user_id,
                      UserModel.username.label('username'),
                      DocumentModel.created_date). \
        filter(DocumentModel.user_id == UserModel.id)

