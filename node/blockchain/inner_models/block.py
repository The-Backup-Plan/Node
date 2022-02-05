from pydantic import root_validator

from node.blockchain.mixins.crypto import HashableMixin, validate_signature_helper
from node.blockchain.mixins.validatable import ValidatableMixin

from ..types import AccountNumber, Signature
from .base import BaseModel
from .block_message import BlockMessage, CoinTransferBlockMessage, GenesisBlockMessage, NodeDeclarationBlockMessage
from .block_message.base import BlockMessageType


class BlockType(BaseModel):
    message: BlockMessageType


class Block(BlockType, HashableMixin, ValidatableMixin):
    signer: AccountNumber
    signature: Signature
    message: BlockMessage

    @classmethod
    def parse_obj(cls, *args, **kwargs):
        if cls is not Block and issubclass(cls, Block):
            return super().parse_obj(*args, **kwargs)

        obj = BlockType.parse_obj(*args, **kwargs)
        type_ = obj.message.type
        from node.blockchain.inner_models.type_map import get_block_subclass
        class_ = get_block_subclass(type_)
        assert class_  # because message.type should be validated by now
        return class_.parse_obj(*args, **kwargs)

    def get_block_number(self):
        return self.message.number

    @root_validator
    def validate_signature(cls, values):
        if cls == Block:  # only child classes signature validation makes sense
            return values

        validate_signature_helper(values)
        return values

    def validate_blockchain_state_dependent(self, blockchain_facade):
        self.message.validate_blockchain_state_dependent(blockchain_facade)


class GenesisBlock(Block):
    message: GenesisBlockMessage


class NodeDeclarationBlock(Block):
    message: NodeDeclarationBlockMessage


class CoinTransferBlock(Block):
    message: CoinTransferBlockMessage
