// This example requires the Places library. Include the libraries=places
// parameter when you first load the API. For example:
// <script
function initMap() {
    var map = new google.maps.Map(document.getElementById("map"), {
      mapTypeControl: false,
      streetViewControl: false,
      fullscreenControl: false,
      center: { lat: -41.640079, lng: 146.315918 },
      zoom: 7,
    });

    new AutocompleteDirectionsHandler(map);
  }


  class AutocompleteDirectionsHandler {
    map;
    originPlaceId;
    destinationPlaceId;
    travelMode;
    directionsService;
    directionsRenderer;
    constructor(map) {
      this.map = map;
      this.originPlaceId = "";
      this.destinationPlaceId = "";
      this.travelMode = google.maps.TravelMode.DRIVING;
      this.directionsService = new google.maps.DirectionsService();
      this.directionsRenderer = new google.maps.DirectionsRenderer();
      this.directionsRenderer.setMap(map);

      const originInput = document.getElementById("origin-input");
      const destinationInput = document.getElementById("destination-input");
      const travelTypeSelector = document.getElementById("travel-type-selector");
      const dateInput = document.getElementById("date-input");
      const submit = document.getElementById("submit");

      // Specify options for autocomplete function
      const options = {
        fields: ["place_id"] ,
        componentRestrictions: {country: "au"}
      };

      // Specify just the place data fields that you need.
      const originAutocomplete = new google.maps.places.Autocomplete(originInput, options);
      // Specify just the place data fields that you need.
      const destinationAutocomplete = new google.maps.places.Autocomplete(
        destinationInput,
        { fields: ["place_id"] }
      );

        // Test
        console.log("Travel mode: " + this.travelMode);

      // this.setupClickListener(
      //   "changemode-walking",
      //   google.maps.TravelMode.WALKING
      // );
      // this.setupClickListener(
      //   "changemode-transit",
      //   google.maps.TravelMode.TRANSIT
      // );
      // this.setupClickListener(
      //   "changemode-driving",
      //   google.maps.TravelMode.DRIVING
      // );
      this.setupPlaceChangedListener(originAutocomplete, "ORIG");
      this.setupPlaceChangedListener(destinationAutocomplete, "DEST");
      this.map.controls[google.maps.ControlPosition.TOP_LEFT].push(originInput);
      this.map.controls[google.maps.ControlPosition.LEFT_TOP].push(destinationInput);
      // this.map.controls[google.maps.ControlPosition.TOP_LEFT].push(travelTypeSelector);
      // this.map.controls[google.maps.ControlPosition.TOP_LEFT].push(dateInput);
      // this.map.controls[google.maps.ControlPosition.TOP_LEFT].push(submit);
    }
    // Sets a listener on a radio button to change the filter type on Places
    // Autocomplete.
    // setupClickListener(id, mode) {
    //   const radioButton = document.getElementById(id);

    //   radioButton.addEventListener("click", () => {
    //     this.travelMode = mode;
    //     this.route();
    //   });
    // }
    setupPlaceChangedListener(autocomplete, mode) {
      autocomplete.bindTo("bounds", this.map);
      autocomplete.addListener("place_changed", () => {
        const place = autocomplete.getPlace();

        if (!place.place_id) {
          window.alert("Please select an option from the dropdown list.");
          return;
        }

        if (mode === "ORIG") {
          this.originPlaceId = place.place_id;
        } else {
          this.destinationPlaceId = place.place_id;
        }

        this.route();
      });
    }
    route() {
      if (!this.originPlaceId || !this.destinationPlaceId) {
        return;
      }

      const me = this;

      this.directionsService.route(
        {
          origin: { placeId: this.originPlaceId },
          destination: { placeId: this.destinationPlaceId },
          travelMode: this.travelMode,
        },
        (response, status) => {
          if (status === "OK") {
            me.directionsRenderer.setDirections(response);
          } else {
            window.alert("Directions request failed due to " + status);
          }
        }
      );
    }
  }