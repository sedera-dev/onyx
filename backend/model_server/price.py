from fastapi import HTTPException,Query, Depends, APIRouter
from pydantic import BaseModel
from typing import Optional
import stripe


router = APIRouter(prefix="/price")


# Secret key stripe
stripe.api_key = "sk_test_51Qk04QLWuxQjMXziLCEIfTUiG4YY3RpXYzN9EtV62zK8W07sKTfBaTslrvriD7jREGfQxVvmcQ6uRVLCn6Jnce9600AMrQ7YVW"

# Class for price creation
class PricingModel(BaseModel):
    name: str
    amount: int
    currency: str = 'usd'  # Par défaut, USD

# Class to filter the price
class PricingFilter(BaseModel):
    active: Optional[bool] = None
    currency: Optional[str] = None
    product_id: Optional[str] = None

# Class metadata
class Metadata(BaseModel):
    order_id: int

# Class to update the price
class PricingUpdate(BaseModel):
    active: Optional[bool] = None
    nickname: Optional[str] = None
    metadata: Optional[Metadata] = None


@router.post("/create-price")
async def create_price(pricing: PricingModel):
    try:
        # Create price
        price = stripe.Price.create(
            unit_amount=pricing.amount,
            currency=pricing.currency,
            product_data={"name": pricing.name},
        )

        # Retrieve associated product details
        product = stripe.Product.retrieve(price.product)

        price.product_data = {
            "id": product.id,
            "name": product.name,
            "type": product.type,
            "object": product.object
        }

        return price
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))



@router.put("/update-price/{price_id}")
async def update_price(price_id: str, pricing: PricingUpdate =  Depends()):
    try:
        # Prepare update parameters
        update_params = {}
        
        # Only include non-None fields in the update
        if pricing.active is not None:
            update_params['active'] = pricing.active
        if pricing.nickname is not None:
            update_params['nickname'] = pricing.nickname
        if pricing.metadata is not None:
            update_params['metadata'] = pricing.metadata.dict()
        
        # If there are parameters to update
        if update_params:
            # Update the price with Stripe
            price = stripe.Price.modify(
                price_id,
                **update_params
            )
            return price
        
        # If no update parameters, retrieve the existing price
        price = stripe.Price.retrieve(price_id)
        return price
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    

@router.get("/get-one-price/{price_id}")
async def get_one_price(price_id: str):
    try:
        price = stripe.Price.retrieve(price_id)

        # Retrieve associated product details
        product = stripe.Product.retrieve(price.product)

        price.product_data = {
            "id": product.id,
            "name": product.name,
            "type": product.type,
            "object": product.object
        }

        return price
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/get-all-price")
async def get_all_price(filter: PricingFilter =  Depends()):
    try:
        # List all prices (with default pagination)
        prices = stripe.Price.list(limit=100) 

        filtered_prices = []

        # Filter price
        for price in prices.data:
            if filter is not None and filter.active is not None and price.active != filter.active: 
                continue

            if filter is not None and filter.currency is not None and price.currency != filter.currency: 
                continue 

            if filter is not None and filter.product_id is not None and price.product != filter.product_id: 
                continue 

            product = stripe.Product.retrieve(price.product)
            price.product_data = {
                "id": product.id,
                "name": product.name,
                "type": product.type,
                "object": product.object
            }

            filtered_prices.append(price)
        return {"prices": filtered_prices}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    




