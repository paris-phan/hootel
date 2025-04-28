from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Loan

# Create your views here.


@login_required
def cancel_booking(request, loan_id):
    loan = get_object_or_404(Loan, id=loan_id)

    if loan:

        # Check if the user is the requester of the loan
        if request.user != loan.requester:
            messages.error(request, "You do not have permission to cancel this booking.")
            return redirect("accounts:user_profile", username=request.user.username)

        # Check if the loan is in a cancellable state (pending)
        if loan.status != 0:  # 0 is pending status
            messages.error(request, "This booking cannot be cancelled.")
            return redirect("accounts:user_profile", username=request.user.username)

        # delete the loan
        loan.delete()

        messages.success(request, "Booking cancelled successfully.")

        # Redirect back to the user's profile
        return redirect("accounts:user_profile", username=request.user.username)

    else:
        messages.error(request, "Booking not found.")
        return redirect("accounts:user_profile", username=request.user.username)


