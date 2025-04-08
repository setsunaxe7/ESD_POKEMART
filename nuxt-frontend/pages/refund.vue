<script setup lang="ts">
import { USelectMenu } from "#components";
import axios from "axios";
import { createClient } from "@supabase/supabase-js";

const SUPABASE_URL = "https://gixgfsneaxermosckfdl.supabase.co";
const SUPABASE_KEY =
  "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImdpeGdmc25lYXhlcm1vc2NrZmRsIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDQwOTg1NDAsImV4cCI6MjA1OTY3NDU0MH0._mg4VE04PMfCIGuF7IVcVca-hZJjyGTdGaMbTP6EnwU";

const supabase = createClient(SUPABASE_URL, SUPABASE_KEY);

const payments = ref([]);
const listings = ref([]);
const selectedTransaction = ref(null);
const selectedReason = ref(null);
const refundReason = ["Card Damaged", "Item not as described", "Others"];
const elaboration = ref("");
const transactionOptions = ref([]);
const imageFile = ref(null);

const handleFileChange = (event: any) => {
  imageFile.value = event.target.files[0];
};

// Get user payments data
const getUserPayments = async () => {
  const userId = "cfacd6c7-074e-4201-9413-6e8ad5bb7997";

  try {
    const response = await axios.get(
      `http://localhost:8000/payment/payments/${userId}`
    );

    if (response.status === 200) {
      console.log("Payment information retrieved successfully:", response.data);
      return response.data.payments;
    }
  } catch (error) {
    console.error("Error fetching payment data:", error);
    throw error;
  }
};

// Get listings based on listing IDs
const getListings = async (listingIds) => {
  try {
    const response = await axios.post(
      "http://localhost:8000/marketplace/api/marketplace/listings/batch",
      { listing_ids: listingIds }
    );

    if (response.status === 200) {
      console.log("Listings retrieved successfully:", response.data);
      return response.data;
    }
  } catch (error) {
    console.error("Error fetching listings:", error);
    throw error;
  }
};

// Format payment data for select menu
const formatPaymentOptions = (paymentsData, listingsData) => {
  const listingMap = {};
  listingsData.forEach((listing) => {
    listingMap[listing.id] = listing;
  });

  return paymentsData
    .filter((payment) => payment.status === "succeeded")
    .map((payment) => {
      const listing = listingMap[payment.listing_id];
      const amount = (payment.amount / 100).toFixed(2);
      return {
        label: `${listing?.title || "Unknown item"} - $${amount}`,
        value: payment.payment_intent_id,
        paymentData: payment,
        listingData: listing,
      };
    });
};

// Submit refund request
const submitRefund = async () => {
  if (!selectedTransaction.value || !selectedReason.value || !imageFile.value) {
    alert("Please fill in all required fields.");
    return;
  }

  const userId = "cfacd6c7-074e-4201-9413-6e8ad5bb7997";
  const transactionId = selectedTransaction.value;
  const reason = selectedReason.value;
  const cardId = selectedTransaction.value.paymentData.listing_id;
  const file = imageFile.value;

  try {
    // Upload image to Supabase
    const fileName = `${Date.now()}_${file.name}`;
    const { error } = await supabase.storage
      .from("refund-photos")
      .upload(fileName, file);

    if (error) {
      console.error("Image upload failed:", error);
      alert("Image upload failed.");
      return;
    }

    const imageURL = `https://gixgfsneaxermosckfdl.supabase.co/storage/v1/object/public/refund-photos/${fileName}`;

    // Send to composite microservice
    await axios.post("http://localhost:8000/refund/refund-process", {
      userId,
      cardId,
      imageURL,
      transactionId: transactionId,
      reason: reason.toLowerCase().includes("damaged")
        ? "damaged"
        : "not as described",
    });

    alert("Refund request submitted successfully!");
  } catch (err) {
    console.error("Submission failed:", err);
    alert("Failed to submit refund request.");
  }
};

onMounted(async () => {
  try {
    const paymentsData = await getUserPayments();
    payments.value = paymentsData || [];
    if (payments.value.length > 0) {
      const listingIds = [
        ...new Set(
          payments.value
            .filter((p) => p.listing_id)
            .map((p) => p.listing_id)
        ),
      ];
      const listingsData = await getListings(listingIds);
      listings.value = listingsData || [];
      transactionOptions.value = formatPaymentOptions(
        payments.value,
        listings.value
      );
    }
  } catch (err) {
    console.error("Failed to initialize page:", err);
  }
});
</script>

<template>
  <UMain class="min-h-[calc(100vh-var(--header-height)-var(--footer-height))]">
    <UContainer>
      <UPageSection
        title="Refund Request"
        description="Submit a refund request for an unsatisfactory order"
        :ui="{ container: 'lg:py-24' }"
      />
      <UCard class="p-4 mb-8">
        <div class="space-y-8">
          <div class="space-y-2">
            <h1 class="text-2xl font-bold">Request form</h1>
            <p class="text-gray-500">
              Fill up this form accordingly to submit a refund request for
              review
            </p>
          </div>
          <div class="grid grid-cols-3 gap-12">
            <div class="col-span-2 flex flex-col space-y-6">
              <div class="space-y-2">
                <p class="font-medium">Choose an order</p>
                <USelectMenu
                  v-model="selectedTransaction"
                  class="w-3/4"
                  :items="transactionOptions"
                  placeholder="Select transaction"
                />
              </div>
              <div class="space-y-2">
                <p class="font-medium">Reason for request</p>
                <USelectMenu
                  v-model="selectedReason"
                  class="w-3/4"
                  :items="refundReason"
                  placeholder="Select reason"
                />
              </div>
              <div class="space-y-2">
                <p class="font-medium">Elaboration for reason</p>
                <UTextarea
                  v-model="elaboration"
                  class="w-3/4"
                  placeholder="Provide a detailed explanation for the reason of this refund request"
                  :rows="4"
                />
              </div>
              <div>
                <p class="font-medium">Upload evidence</p>
                <UInput class="mt-2" type="file" @change="handleFileChange" />
              </div>
            </div>
          </div>
        </div>
      </UCard>
      <div class="w-full flex">
        <UButton
          size="xl"
          :block="true"
          class="w-1/2 m-auto"
          @click="submitRefund"
        >
          Submit Request
        </UButton>
      </div>
    </UContainer>
  </UMain>
</template>
